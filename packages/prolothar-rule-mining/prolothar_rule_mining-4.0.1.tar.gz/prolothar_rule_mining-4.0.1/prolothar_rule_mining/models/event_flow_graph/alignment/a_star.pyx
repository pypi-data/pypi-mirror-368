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

import heapq

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment import Alignment
from prolothar_rule_mining.models.event_flow_graph.alignment.heuristics import Heuristic
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder import AlignmentFinder
from prolothar_rule_mining.models.event_flow_graph.alignment.partial_alignment import PartialAlignment

class AStar(AlignmentFinder):

    def __init__(self, graph: EventFlowGraph, heuristic: Heuristic):
        super().__init__(graph)
        self.__heuristic = heuristic

    def compute_alignment(self, sequence: Tuple[str]) -> Alignment:
        openlist = []
        heapq.heappush(openlist, PartialAlignment(
            Alignment(), self.graph.source, 0, 0, len(sequence)+1))

        while openlist:
            current = heapq.heappop(openlist)
            if current.node is self.graph.sink \
            and current.event_index >= len(sequence):
                return current.alignment
            for neighbor in current.yield_neighbors(
                    sequence, self.__heuristic, self.graph.sink):
                heapq.heappush(openlist, neighbor)

        raise NotImplementedError('should never reach this point')
