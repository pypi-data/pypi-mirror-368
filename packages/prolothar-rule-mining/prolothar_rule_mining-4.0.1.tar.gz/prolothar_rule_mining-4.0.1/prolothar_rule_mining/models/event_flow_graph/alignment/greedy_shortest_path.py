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
from typing import List, Tuple

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node
from prolothar_rule_mining.models.event_flow_graph.caching import CachedShortestPathsToEventFinder
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment import Alignment
from prolothar_rule_mining.models.event_flow_graph.alignment.heuristics import Heuristic
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder import AlignmentFinder

class GreedyShortestPath(AlignmentFinder):

    def __init__(self, graph: EventFlowGraph, heuristic: Heuristic):
        super().__init__(graph)
        self.__heuristic = heuristic
        self.__find_shortest_paths_finder = CachedShortestPathsToEventFinder(graph)

    def compute_alignment(self, sequence: Tuple[str]) -> Alignment:
        alignment = Alignment()
        last_node = self.graph.source
        for i,event in enumerate(sequence):
            next_node = self.__align_event(event, i, last_node, alignment, sequence)
            last_node = next_node

        self.__align_event(self.graph.sink.event, len(sequence), last_node,
                           alignment, sequence)
        return alignment

    def __align_event(
            self, event: str, event_index: int, current_node: Node,
            alignment: Alignment, sequence: Tuple[str]) -> Node:
        list_of_paths_to_next_node = self.__find_shortest_paths_finder(current_node, event)

        if list_of_paths_to_next_node:
            selected_path = self.__select_path_to_next_node(
                list_of_paths_to_next_node, event_index, sequence)
            current_node = self.__skip_intermediate_nodes(selected_path, alignment)
            alignment.append_sync_move(current_node, event_index)
        else:
            alignment.append_log_move(event_index)

        return current_node

    def __select_path_to_next_node(
            self, list_of_paths_to_next_node: List[List[Node]],
            event_index: int, sequence: Tuple[str]) -> List[Node]:
        while len(list_of_paths_to_next_node) > 1 and event_index < len(sequence):
            event_index += 1
            heuristic_list = []
            best_heuristic = float('inf')

            for path in list_of_paths_to_next_node:
                heuristic = self.__heuristic(path[1], event_index, sequence)
                if heuristic < best_heuristic:
                    best_heuristic = heuristic
                heuristic_list.append(heuristic)
            list_of_paths_to_next_node = [
                path for path, heuristic
                in zip(list_of_paths_to_next_node, heuristic_list)
                if heuristic == best_heuristic]
        return list_of_paths_to_next_node[0]

    def __skip_intermediate_nodes(
            self, path_to_next_node: List[Node], alignment: Alignment) -> Node:
        for node in path_to_next_node[1:-1]:
            alignment.append_model_move(node)
        return path_to_next_node[-1]
