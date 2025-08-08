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
this module contains the Node model of an EventFlowGraph
"""

cdef class Node:
    """
    node of a an event flow graph. the nodes have an id and an event
    """

    def __init__(self, node_id: int, event: str):
        self.node_id = node_id
        self.event = event
        #Set[Node]
        self.children = set()
        #Set[Node]
        self.parents = set()
        self.attributes = {}

    def __getstate__(self):
        """
        avoid pickling sets (children, parents) because when unpickling
        this will lead to an error when the hash function is called for
        set construction:
        https://stackoverflow.com/questions/44887394/pickle-dill-cannot-handle-circular-references-if-hash-is-overridden
        https://bugs.python.org/issue1761028
        """
        return (self.node_id, self.event, tuple(self.children),
                tuple(self.parents), self.attributes)

    def __setstate__(self, state):
        self.node_id = state[0]
        self.event = state[1]
        self.children = tuple(state[2])
        self.parents = tuple(state[3])
        self.attributes = state[4]

    def __hash__(self) -> int:
        return self.node_id

    def __eq__(self, other) -> bool:
        return isinstance(other, Node) and self.node_id == (<Node>other).node_id

    def __repr__(self) -> str:
        return 'Node(%d, %r)' % (self.node_id, self.event)
