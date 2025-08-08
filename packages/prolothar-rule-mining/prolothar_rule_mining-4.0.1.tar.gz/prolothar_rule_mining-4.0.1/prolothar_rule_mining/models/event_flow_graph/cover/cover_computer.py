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
this module contains classes and methods to compute a cover
"""

from prolothar_common.models.dataset import Dataset
from prolothar_common.models.dataset.instance import TargetSequenceInstance
from prolothar_rule_mining.models.event_flow_graph.graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph.node import Node
from prolothar_rule_mining.models.event_flow_graph.cover.cover import Cover
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder import AlignmentFinder
from prolothar_rule_mining.models.event_flow_graph.alignment.petrinet import PetrinetAligner

class CoverComputer:
    def __init__(
            self, graph: EventFlowGraph, assign_instances_to_edges: bool = False,
            alignment_finder: AlignmentFinder = None):
        self.__graph: EventFlowGraph = graph
        if alignment_finder is None:
            self.__aligner = PetrinetAligner(graph)
        else:
            self.__aligner = alignment_finder
        self.__assign_instances_to_edges = assign_instances_to_edges

    def compute_cover(self, dataset: Dataset) -> Cover:
        if self.__assign_instances_to_edges:
            for edge in self.__graph.edges():
                edge.attributes['instances'] = set()
                edge.attributes['nr_of_instances'] = 0

        cover = Cover(dataset.get_set_of_sequence_symbols(),
                      self.__graph.sink.event)

        for instance in dataset:
            self.extend_cover(cover, instance)

        return cover

    def extend_cover(self, cover: Cover, instance: TargetSequenceInstance):
        try:
            self.__extend_cover_for_known_sequence(cover, instance)
        except KeyError:
            self.__extend_cover_for_unseen_sequence(cover, instance)

    def __extend_cover_for_known_sequence(
            self, cover: Cover, instance: TargetSequenceInstance):
        cover_steps = cover.get_steps_for_sequence(instance.get_target_sequence())
        node = self.__graph.source
        for step in cover_steps:
            step.execute()
            if node is not step.current_node:
                self.__add_instance_to_edge(instance, node, step.current_node)
            node = step.current_node
        self.__add_instance_to_edge(instance, node, self.__graph.sink)

    def __extend_cover_for_unseen_sequence(
            self, cover: Cover, instance: TargetSequenceInstance):
        sequence = instance.get_target_sequence()
        cover.start_recording_for_sequence(sequence)
        alignment = self.__aligner.compute_alignment(sequence)
        node = self.__graph.source

        for move in alignment:
            if move.is_model_move():
                cover.add_redundant_event(node, move.node.event)
                self.__add_instance_to_edge(instance, node, move.node)
                node = move.node
            elif move.is_log_move():
                cover.add_missed_event(node, sequence[move.event_index])
            else:
                cover.add_matched_event(node, move.node.event)
                self.__add_instance_to_edge(instance, node, move.node)
                node = move.node
        cover.end_recording_for_sequence()

    def __add_instance_to_edge(self, instance: TargetSequenceInstance, last_node: Node, next_node: Node):
        if self.__assign_instances_to_edges:
            edge = self.__graph.get_edge(last_node, next_node)
            set_of_instances = edge.attributes['instances']
            set_of_instances.add(instance)
            edge.attributes['nr_of_instances'] = len(set_of_instances)

def compute_cover(dataset: Dataset, graph: EventFlowGraph,
                  assign_instances_to_edges: bool = False,
                  alignment_finder: AlignmentFinder = None) -> Cover:
    return CoverComputer(
        graph, assign_instances_to_edges=assign_instances_to_edges,
        alignment_finder=alignment_finder
    ).compute_cover(dataset)
