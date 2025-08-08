'''
    This file is part of Prolothar-Rule-Mining (More Info: https://github.com/shs-it/prolothar-rule-mining).

    Prolothar-Rule-Mining is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Prolothar-Rule-Mining is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Prolothar-Rule-Mining. If not, see <https://www.gnu.org/licenses/>.
'''
"""
this module contains the event flow graph miner, i.e. for a given dataset an
event flow graph is inferred
"""

from typing import Callable, Tuple
import sys

from prolothar_common.collections import list_utils

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.models.dataset.instance import TargetSequenceInstance
from prolothar_common.func_tools import do_nothing

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph.cover import Cover
from prolothar_rule_mining.models.event_flow_graph.cover import compute_cover
from prolothar_rule_mining.models.event_flow_graph.cover import CoverComputer
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder import AlignmentFinder
from prolothar_rule_mining.models.event_flow_graph.alignment.petrinet import PetrinetAligner

from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.event_flow_graph_miner.abstract import EventFlowGraphMiner
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.event_flow_graph_miner.sequence_alignment_no_mdl import SequenceAlignmentNoMdl
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates import Candidate
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates import CandidateQueue
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates import NotApplicableError
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates import RemoveChainCandidate
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates import RemoveEdgeCandidate

class SequenceTopDownEventFlowGraphMiner(EventFlowGraphMiner):
    """
    infers an EventFlowGraph from a given sequential dataset.
    we start with an overfitting graph computed from "SequenceAlignmentNoMdl"
    and tries to iteratively prune the graph
    """

    def __init__(
        self, logger: Callable[[str],None] = print, exact_mdl: bool = True,
        alignment_finder_factory_score: Callable[[EventFlowGraph], AlignmentFinder] = None,
        patience: int = sys.maxsize):
        """
        creates a new EventFlowGraphMiner
        """
        self.__logger = logger if logger is not None else do_nothing
        self.__exact_mdl = exact_mdl

        if alignment_finder_factory_score is None:
            self.__alignment_finder_factory_score = PetrinetAligner
        else:
            self.__alignment_finder_factory_score = alignment_finder_factory_score

        self.__patience = patience

    def mine_event_flow_graph(self, dataset: TargetSequenceDataset) -> EventFlowGraphMiner:
        graph = SequenceAlignmentNoMdl(logger=self.__logger).mine_event_flow_graph(dataset)

        current_mdl, cover = self.__compute_mdl(graph, dataset)
        self.__logger('start pruning with MDL %.2f' % current_mdl)

        self.__logger('start to search for graph pruning')
        candidates = self.__initialize_candidates(graph)
        current_mdl = self.__apply_candidates_iteratively(
            candidates, current_mdl, cover, dataset, graph)

        self.__logger('correct MDL: %.2f' % self.__compute_mdl(graph, dataset)[0])

        self.__logger('remove branches not used by the cover')
        graph.remove_edges_without_instances()

        return graph

    def __apply_candidates_iteratively(
            self, candidates: CandidateQueue, current_mdl: float, cover: Cover,
            dataset: TargetSequenceDataset, graph: EventFlowGraph) -> float:
        nr_of_successively_discarded_candidates = 0
        while candidates.is_not_empty():
            top_candidate: Candidate = candidates.pop()
            if not top_candidate.leads_to_cycle():
                try:
                    if self.__exact_mdl:
                        top_candidate.apply()
                        candidate_mdl,_ = self.__compute_mdl(graph, dataset)
                    else:
                        top_candidate.apply()
                        cached_cover_steps, invalidated_instances = \
                            self.__change_cover(top_candidate, graph, cover)
                        candidate_mdl = graph.compute_mdl(
                            dataset.get_set_of_sequence_symbols()) + cover.compute_mdl()
                    if candidate_mdl < current_mdl:
                        current_mdl = candidate_mdl
                        self.__logger('improved MDL to %.2f' % current_mdl)
                        self.__add_new_candidates(candidates, top_candidate, graph)
                        nr_of_successively_discarded_candidates = 0
                    else:
                        self.__logger('candidate could not improve MDL: %.2f' % candidate_mdl)
                        if self.__exact_mdl:
                            top_candidate.undo()
                        else:
                            self.__restore_cover(
                                top_candidate, graph, cover, cached_cover_steps,
                                invalidated_instances)
                        nr_of_successively_discarded_candidates += 1
                except NotApplicableError:
                    pass

            if nr_of_successively_discarded_candidates > self.__patience:
                self.__logger('early stopping')
                break
        return current_mdl

    def __initialize_candidates(
            self, graph: EventFlowGraph) -> CandidateQueue:
        candidates = CandidateQueue()
        for chain in graph.find_chains(min_length=1):
            candidates.add(RemoveChainCandidate(graph, chain))
        for edge in graph.edges():
            candidates.add(RemoveEdgeCandidate(graph, edge))
        return candidates

    def __change_cover(
            self, top_candidate: Candidate, graph: EventFlowGraph, cover: Cover):
        invalidated_instances = set()
        invalidated_sequences = set()
        for edge in top_candidate.get_removed_edges():
            for instance in edge.attributes['instances']:
                invalidated_instances.add(instance)
                invalidated_sequences.add(instance.get_target_sequence())

        for instance in invalidated_instances:
            for step in cover.get_steps_for_sequence(instance.get_target_sequence()):
                step.undo()

        cached_cover_steps = {
            sequence: cover.get_steps_for_sequence(sequence)
            for sequence in invalidated_sequences
        }

        for sequence in invalidated_sequences:
            cover.clear_steps_for_sequence(sequence)

        cover_computer = CoverComputer(
            graph, assign_instances_to_edges=True,
            alignment_finder=self.__alignment_finder_factory_score(graph))

        for instance in invalidated_instances:
            cover_computer.extend_cover(cover, instance)

        top_candidate.post_process_cover_after_apply(cover)

        return cached_cover_steps, invalidated_instances

    def __restore_cover(
            self, candidate: Candidate, graph: EventFlowGraph, cover: Cover,
            cached_cover_steps, invalidated_instances):
        for instance in invalidated_instances:
            last_node = graph.source
            for step in cover.get_steps_for_sequence(instance.get_target_sequence()):
                step.undo()
                if last_node is not step.current_node:
                    edge = graph.get_edge(last_node, step.current_node)
                    edge.attributes['nr_of_instances'] -= 1
                    edge.attributes['instances'].discard(instance)
                    last_node = step.current_node
            edge = graph.get_edge(last_node, graph.sink)
            edge.attributes['nr_of_instances'] -= 1
            edge.attributes['instances'].discard(instance)

        candidate.undo()

        for sequence, steps in cached_cover_steps.items():
            cover.set_steps_for_sequence(steps, sequence)

        cover_computer = CoverComputer(graph, assign_instances_to_edges=True)

        for instance in invalidated_instances:
            cover_computer.extend_cover(cover, instance)

    def __add_new_candidates(
            self, candidates: CandidateQueue, last_applied_candidate: Candidate,
            graph: EventFlowGraph):
        for new_candidate in last_applied_candidate.yield_new_candidates(graph):
            candidates.add(new_candidate)

    def __compute_mdl(
            self, graph: EventFlowGraph, dataset: TargetSequenceDataset,
            verbose=False, assign_instances_to_edges: bool = True) -> Tuple[float, Cover]:
        mdl_of_model = graph.compute_mdl(dataset.get_set_of_sequence_symbols())
        cover = compute_cover(dataset, graph,
                              assign_instances_to_edges=assign_instances_to_edges,
                              alignment_finder=self.__alignment_finder_factory_score(graph))
        mdl_of_data = cover.compute_mdl()
        if verbose:
            print((mdl_of_model, mdl_of_data))
            print(cover.count_model_codes())
        return mdl_of_model + mdl_of_data, cover

    def __repr__(self) -> str:
        return 'SequenceTopDownEventFlowGraphMiner(exact_mdl=%r)' % self.__exact_mdl
