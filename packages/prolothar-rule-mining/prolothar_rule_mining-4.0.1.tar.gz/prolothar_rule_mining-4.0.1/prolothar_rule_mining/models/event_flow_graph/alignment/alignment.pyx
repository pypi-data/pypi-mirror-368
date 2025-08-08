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
from typing import Union

from prolothar_rule_mining.models.event_flow_graph cimport Node
from prolothar_rule_mining.models.event_flow_graph import Node as PyNode

cdef class Move:
    def __init__(self, node: Union[PyNode,None], event_index: Union[int,None]):
        self.node: Union[PyNode,None] = node
        self.event_index: Union[int,None] = event_index

    cpdef bint is_model_move(self):
        return self.event_index is None

    cpdef bint is_log_move(self):
        return self.node is None

    cpdef bint is_sync_move(self):
        return self.node is not None and self.event_index is not None

    def __eq__(self, other: 'Move') -> bool:
        return self is other or (
            self.node == other.node and self.event_index == other.event_index)

    def __repr__(self) -> str:
        return '(%r,%r)' % (self.node, self.event_index)

cdef class Alignment:

    def __init__(self):
        self.moves = []

    def __eq__(self, other: 'Alignment') -> bool:
        return self is other or self.moves == other.moves

    cpdef append_log_move(self, int event_index):
        self.moves.append(Move(None, event_index))

    cpdef append_model_move(self, Node node):
        self.moves.append(Move(node, None))

    cpdef append_sync_move(self, Node node, int event_index):
        self.moves.append(Move(node, event_index))

    cpdef Move get_last_move(self):
        return self.moves[-1]

    def __repr__(self) -> str:
        return str(self.moves)

    def __len__(self):
        return len(self.moves)

    def __iter__(self):
        yield from self.moves

    cpdef Alignment copy(self):
        cdef Alignment copy = Alignment()
        copy.moves = list(self.moves)
        return copy
