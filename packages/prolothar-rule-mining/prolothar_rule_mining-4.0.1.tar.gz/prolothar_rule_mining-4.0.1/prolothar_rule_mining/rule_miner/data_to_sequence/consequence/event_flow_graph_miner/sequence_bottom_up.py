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

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.func_tools import do_nothing

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder import AlignmentFinder
from prolothar_rule_mining.models.event_flow_graph.alignment.greedy_shortest_path import GreedyShortestPath
from prolothar_rule_mining.models.event_flow_graph.alignment.heuristics import ReachabilityHeuristic
from prolothar_rule_mining.models.event_flow_graph.cover import CoverComputer

from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.event_flow_graph_miner.abstract import EventFlowGraphMiner
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates import AddSequencePathCandidate

class SequenceBottomUpEventFlowGraphMiner(EventFlowGraphMiner):
    """
    infers an EventFlowGraph from a given sequential dataset.
    we start with an empty graph and greedily add paths for unexplained
    sequences.
    """

    def __init__(self, logger: Callable[[str], None] = print,
                 alignment_finder_factory_model_extension: Callable[[EventFlowGraph], AlignmentFinder] = None,
                 alignment_finder_factory_score: Callable[[EventFlowGraph], AlignmentFinder] = None,
                 add_edge_from_source_to_sink: bool = False,
                 discard_failed_candidates: bool = False,
                 patience: int = sys.maxsize):
        """
        creates a new EventFlowGraphMiner
        """
        self.__logger = logger if logger is not None else do_nothing
        if alignment_finder_factory_model_extension is None:
            self.__alignment_finder_factory_model_extension = lambda graph: GreedyShortestPath(
                graph, ReachabilityHeuristic(graph))
        else:
            self.__alignment_finder_factory_model_extension = alignment_finder_factory_model_extension
        if alignment_finder_factory_score is None:
            self.__alignment_finder_factory_score = lambda graph: GreedyShortestPath(
                graph, ReachabilityHeuristic(graph))
        else:
            self.__alignment_finder_factory_score = alignment_finder_factory_score
        self.__patience = patience
        self.__add_edge_from_source_to_sink = add_edge_from_source_to_sink
        self.__discard_failed_candidates = discard_failed_candidates

    def mine_event_flow_graph(self, dataset: TargetSequenceDataset) -> EventFlowGraphMiner:
        graph, current_mdl = self.__initialize_search(dataset)

        candidates_without_improvement = []

        for sequence in reversed(dataset.get_sequences_ordered_by_frequency()):
            candidate_transformation = AddSequencePathCandidate(
                graph, sequence,
                alignment_finder=self.__alignment_finder_factory_model_extension(graph))
            candidate_transformation.apply()

            candidate_mdl = self.__compute_mdl(graph, dataset)
            if candidate_mdl < current_mdl:
                candidates_without_improvement.clear()
                current_mdl = candidate_mdl
                self.__logger('new best MDL: %.2f' % candidate_mdl)
            else:
                if self.__discard_failed_candidates:
                    candidate_transformation.undo()
                candidates_without_improvement.append(candidate_transformation)
                if len(candidates_without_improvement) > self.__patience:
                    self.__logger('early stopping')
                    break
        else:
            self.__logger('no more sequences left')

        if not self.__discard_failed_candidates:
            for bad_candidate in reversed(candidates_without_improvement):
                bad_candidate.undo()

        graph.merge_redundant_nodes()

        if graph.get_nr_of_edges() == 0:
            graph.add_edge(graph.source, graph.sink)

        return graph

    def __initialize_search(self, dataset: TargetSequenceDataset) -> Tuple[EventFlowGraph, float]:
        graph = EventFlowGraph()
        source_to_sink_edge = graph.add_edge(graph.source, graph.sink)
        current_mdl = self.__compute_mdl(graph, dataset)
        self.__logger('start MDL: %.2f' % current_mdl)
        if not self.__add_edge_from_source_to_sink:
            graph.remove_edge(source_to_sink_edge)
        return graph, current_mdl

    def __compute_mdl(
            self, graph: EventFlowGraph, dataset: TargetSequenceDataset) -> float:
        mdl_of_model = graph.compute_mdl(dataset.get_set_of_sequence_symbols())
        cover = CoverComputer(
            graph, alignment_finder=self.__alignment_finder_factory_score(graph)
        ).compute_cover(dataset)
        self.__logger(cover.count_model_codes())
        mdl_of_data = cover.compute_mdl()
        return mdl_of_model + mdl_of_data

    def __repr__(self) -> str:
        return 'SequenceBottomUpEventFlowGraphMiner(%r,%r,%r)' % (
            self.__alignment_finder_factory_model_extension,
            self.__alignment_finder_factory_score,
            self.__patience)