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
from typing import Tuple

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder import AlignmentFinder
from prolothar_rule_mining.models.event_flow_graph.alignment.greedy_shortest_path import GreedyShortestPath
from prolothar_rule_mining.models.event_flow_graph.alignment.heuristics import ReachabilityHeuristic

from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates import Candidate

class AddSequencePathCandidate(Candidate):
    """
    adds a path to the graph to match a given sequence
    """
    def __init__(self, graph: EventFlowGraph, sequence: Tuple[str],
                 alignment_finder: AlignmentFinder = None):
        super().__init__(graph, None)
        if alignment_finder is None:
            self.__alignment_finder = GreedyShortestPath(
                graph, ReachabilityHeuristic(graph))
        else:
            self.__alignment_finder = alignment_finder

        self.__sequence = sequence
        self.__graph = graph

    def _apply(self):
        if self.__graph.get_nr_of_edges() == 0:
            self.__add_path_for_empty_graph()
        else:
            self.__add_path_for_none_empty_graph()

    def __add_path_for_empty_graph(self):
        last_node = self.__graph.source
        for event in self.__sequence:
            new_node = self._add_node(event)
            self._add_edge(last_node, new_node)
            last_node = new_node
        self.__graph.add_edge(last_node, self.__graph.sink)

    def __add_path_for_none_empty_graph(self):
        last_node = self.__graph.source
        for move in self.__alignment_finder.compute_alignment(self.__sequence):
            if move.is_log_move():
                if move.event_index < len(self.__sequence):
                    new_node = self._add_node(self.__sequence[move.event_index])
                else:
                    new_node = self.__graph.sink
                self._add_edge(last_node, new_node)
                last_node = new_node
            elif move.is_sync_move():
                if move.node not in last_node.children:
                    self._add_edge(last_node, move.node)
                last_node = move.node

    def leads_to_cycle(self) -> bool:
        return False