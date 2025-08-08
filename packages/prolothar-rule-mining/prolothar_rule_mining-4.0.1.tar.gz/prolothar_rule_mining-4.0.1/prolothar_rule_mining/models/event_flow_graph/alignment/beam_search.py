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
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment import Alignment
from prolothar_rule_mining.models.event_flow_graph.alignment.heuristics import Heuristic
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder import AlignmentFinder

from prolothar_rule_mining.models.event_flow_graph.alignment.partial_alignment import PartialAlignment

class BeamSearch(AlignmentFinder):

    def __init__(self, graph: EventFlowGraph, heuristic: Heuristic, beam_width: int,
                 model_move_cost: int = 1):
        super().__init__(graph)
        self.__heuristic = heuristic
        if beam_width < 1:
            raise ValueError('beam_width must not be < 1 but was %d' % beam_width)
        self.__beam_width = beam_width
        self.__model_move_cost = model_move_cost

    def compute_alignment(self, sequence: Tuple[str]) -> Alignment:
        candidates = [PartialAlignment(
            Alignment(), self.graph.source, 0, 0,
            self.__heuristic(self.graph.source, 0, sequence))]
        while True:
            new_candidates = []
            for candidate in candidates:
                if candidate.node is self.graph.sink:
                    return candidate.alignment
                new_candidates.extend(candidate.yield_neighbors(
                    sequence, self.__heuristic, self.graph.sink,
                    model_move_cost = self.__model_move_cost))
            new_candidates.sort()
            candidates = new_candidates[:self.__beam_width]
