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
this module contains the Edge model of an EventFlowGraph
"""

from prolothar_rule_mining.models.event_flow_graph.node import Node

class Edge:
    """
    edge of a an event flow graph. the edge has a from and a to node
    """
    __slots__ = ('from_node', 'to_node', 'attributes')

    def __init__(self, from_node: Node, to_node: Node):
        self.from_node = from_node
        self.to_node = to_node
        self.attributes = {}

    def __hash__(self) -> int:
        return hash((self.from_node, self.to_node))

    def __eq__(self, other: 'Edge') -> int:
        return self is other or (
            self.from_node == other.from_node and self.to_node == other.to_node)

    def __repr__(self) -> str:
        return '(%r, %r)' % (self.from_node, self.to_node)
