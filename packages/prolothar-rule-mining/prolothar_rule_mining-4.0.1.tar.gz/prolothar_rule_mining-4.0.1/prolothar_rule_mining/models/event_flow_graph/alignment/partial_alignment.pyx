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
from typing import Generator

from prolothar_rule_mining.models.event_flow_graph.node cimport Node
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment cimport Alignment
from prolothar_rule_mining.models.event_flow_graph.alignment.heuristics import Heuristic

cdef class PartialAlignment():
    cdef public Node node
    cdef public Alignment alignment
    cdef public int event_index
    cdef public int cost
    cdef public int heuristic
    cdef public int f_score

    def __cinit__(
            self, Alignment alignment, Node node, int event_index, int cost,
            int heuristic):
        self.alignment = alignment
        self.node = node
        self.cost = cost
        self.heuristic = heuristic
        self.event_index = event_index
        self.f_score = self.cost + self.heuristic

    def __lt__(self, other: 'PartialAlignment') -> bool:
        return self.f_score < other.f_score

    cpdef PartialAlignment extend_with_model_move(
            self, Node node, int heuristic,
            int model_move_cost = 1):
        alignment = self.alignment.copy()
        alignment.append_model_move(node)
        return PartialAlignment(
            alignment,
            node,
            self.event_index,
            self.cost + model_move_cost,
            heuristic
        )

    cpdef PartialAlignment extend_with_log_move(self, int heuristic):
        alignment = self.alignment.copy()
        alignment.append_log_move(self.event_index)
        return PartialAlignment(
            alignment,
            self.node,
            self.event_index + 1,
            self.cost + 1,
            heuristic
        )

    cpdef PartialAlignment extend_with_sync_move(self, Node node, int heuristic):
        alignment = self.alignment.copy()
        alignment.append_sync_move(node, self.event_index)
        return PartialAlignment(
            alignment,
            node,
            self.event_index + 1,
            self.cost,
            heuristic
        )

    def yield_neighbors(
            self, sequence: Tuple[str], heuristic: Heuristic, Node sink,
            model_move_cost: int = 1) -> Generator['PartialAlignment',None,None]:
        if self.node is not sink:
            for child in self.node.children:
                #move to sink only allowed if sequence is covered
                if (child is not sink or self.event_index > len(sequence)) \
                and not (len(self.alignment) > 0 and
                         self.alignment.get_last_move().is_log_move() and
                         self.event_index < len(sequence) and
                         sequence[self.event_index] == child.event):
                    yield self.extend_with_model_move(
                        child, heuristic(child, self.event_index, sequence),
                        model_move_cost=model_move_cost)
                #we have to make sure that we always can reach the sink even
                #if the search space has been pruned
                elif len(self.alignment) > 0 and self.alignment.get_last_move().is_model_move():
                    yield self.extend_with_log_move(
                        heuristic(self.node, self.event_index+1, sequence))
        #do not allow log move after model move, because model move followed by
        #a log move is equivalent => prunes the search space
        if not (len(self.alignment) > 1 and self.alignment.get_last_move().is_model_move()) \
        and self.event_index < len(sequence):
            yield self.extend_with_log_move(
                heuristic(self.node, self.event_index+1, sequence))

        try:
            next_event = sequence[self.event_index]
        except IndexError:
            next_event = sink.event

        for child in self.node.children:
            if child.event == next_event:
                yield self.extend_with_sync_move(
                    child, heuristic(child, self.event_index+1, sequence))