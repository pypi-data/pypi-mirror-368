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
from typing import Tuple, Set, List, Generator

from abc import ABC, abstractmethod

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node, Edge
from prolothar_rule_mining.models.event_flow_graph.cover import Cover

class Candidate(ABC):
    """
    template for change operations on an EventFlowGraph during search for an
    EventFlowGraph given a Dataset (set of sequences)
    """

    def __init__(self, graph: EventFlowGraph, priority: Tuple):
        self.__graph = graph
        self.__priority = priority
        self.__applied = False
        self.__added_edges: Set[Edge] = set()
        self.__added_nodes: Set[Node] = set()
        self.__removed_nodes: Set[Node] = set()
        self.__removed_edges: Set[Edge] = set()

    def apply(self):
        """
        applies this candidate

        Raises
        ------
        ValueError
            if the candidate already has been applied
        """
        if self.__applied:
            raise ValueError('already applied')
        self.__applied = True
        self._apply()

    @abstractmethod
    def _apply(self):
        """
        applies the candidate using the transformation methods defined in
        candidate.py
        """

    def undo(self):
        """
        reverts the changes of this candidate

        Raises
        ------
        ValueError
            if the candidate already has not been applied before
        """
        if not self.__applied:
            raise ValueError('not applied yet')

        for edge in self.__added_edges:
            self.__graph.remove_edge(edge)
        for node in self.__added_nodes:
            self.__graph.remove_node(node)

        for node in self.__removed_nodes:
            self.__graph.add_removed_node(node)
        for edge in self.__removed_edges:
            self.__graph.add_removed_edge(edge)

        self.__added_nodes.clear()
        self.__added_edges.clear()
        self.__removed_nodes.clear()
        self.__removed_edges.clear()

        self.__applied = False

    @abstractmethod
    def leads_to_cycle(self) -> bool:
        """
        returns True if the application of this candidate introduces a cycle
        in the eventflow graph
        """

    def _add_node(self, event: str) ->  Node:
        """
        creates a new node with the given event in the graph.
        the addition of the node is recorded such that undo() will be able to
        remove the node.
        """
        node = self.__graph.add_node(event)
        self.__added_nodes.add(node)
        return node

    def _remove_node(self, node: Node):
        """
        removes a node from the graph.
        the removal of the node is recorded such that undo() will be able to
        re-add the node.
        """
        self.__graph.remove_node(node)
        self.__removed_nodes.add(node)
        return node

    def _add_edge(self, from_node: Node, to_node: Node):
        """
        creates a new edge in the graph.
        the addition of the edge is recorded such that undo() will be able to
        remove the edge.
        """
        edge = self.__graph.add_edge(from_node, to_node)
        edge.attributes['instances'] = set()
        edge.attributes['nr_of_instances'] = 0
        self.__added_edges.add(edge)

    def _remove_edge(self, from_node: Node, to_node: Node):
        """
        removes an edge from the graph.
        the removal of the edge is recorded such that undo() will be able to
        re-add the edge.
        """
        removed_edge = self.__graph.get_edge(from_node, to_node)
        if removed_edge not in self.__added_edges:
            self.__graph.remove_edge(removed_edge)
            self.__removed_edges.add(removed_edge)
        else:
            self.__added_edges.remove(removed_edge)

    def get_removed_edges(self) -> Set[Edge]:
        return self.__removed_edges

    def get_added_edges(self) -> Set[Edge]:
        return self.__added_edges

    def get_removed_nodes(self) -> Set[Node]:
        return self.__removed_nodes

    def _find_shortest_path(self, from_node: Node, to_node: Node) -> List[Node]:
        return self.__graph.find_shortest_path(from_node, to_node)

    def _graph_contains_node(self, node: Node):
        return self.__graph.contains_node(node)

    def _graph_contains_edge(self, edge: Edge):
        return self.__graph.contains_edge(edge)

    def _sink_is_reachable_from_source(self) -> bool:
        return bool(self.__graph.find_shortest_path(
            self.__graph.source, self.__graph.sink))

    def yield_new_candidates(
            self, graph: EventFlowGraph) -> Generator['Candidate', None, None]:
        return
        yield

    def post_process_cover_after_apply(self, cover: Cover):
        """
        can be overriden for better mdl estimations
        """
        pass

    def __lt__(self, other: 'Candidate'):
        return self.__priority < other.__priority