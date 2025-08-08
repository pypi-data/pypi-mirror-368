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
module of the EventFlowGraph model
"""

from typing import Generator, Set, Union, List, Callable, Dict, Tuple

from collections import deque, defaultdict
import itertools

import json

from math import log2
from prolothar_common import mdl_utils

import networkx as nx
from graphviz import Digraph
from prolothar_common import gviz_utils

from prolothar_rule_mining.models.event_flow_graph.node import Node
from prolothar_rule_mining.models.event_flow_graph.edge import Edge

class EventFlowGraph:
    """
    an event flow graph, i.e. a directed graph whose nodes are events with two
    special nodes (source and sink).
    """

    def __init__(self):
        self.__node_id_generator: Generator[int,None,None] = iter(range(100000))
        self.source = Node(next(self.__node_id_generator), 'ε')
        self.sink = Node(next(self.__node_id_generator), 'ω')
        self.__nodes: Dict[int, Node] = {}
        self.__edges: Dict[Tuple[Node,Node], Edge] = {}

    def get_nr_of_nodes(self) -> int:
        """
        returns the number of nodes in this graph. source and sink node are not
        included
        """
        return len(self.__nodes)

    def get_nr_of_edges(self) -> int:
        return len(self.__edges)

    def add_node(self, event: str) -> Node:
        """
        adds a new node with the given event to this graph

        Parameters
        ----------
        event : str
            event of the node that is supposed to be created and added to the graph

        Returns
        -------
        Node
            the created node
        """
        node = Node(next(self.__node_id_generator), event)
        self.__nodes[node.node_id] = node
        return node

    def contains_node(self, node: Node) -> bool:
        """
        returns True iff this graph contains the given node
        """
        return node.node_id in self.__nodes or node in (self.source, self.sink)

    def contains_edge(self, edge: Edge) -> bool:
        """
        returns True iff this graph contains the given edge
        """
        return (edge.from_node, edge.to_node) in self.__edges

    def get_node_by_id(self, node_id: int) -> Node:
        """
        retrieves a node by id. if no such node exists, a KeyError is raised
        """
        return self.__nodes[node_id]

    def add_removed_node(self, node: Node):
        """
        adds an existing node instance to this graph

        Parameters
        ----------
        node : Node
            The node will added to this graph. It is not allowed to have any edges.
            Otherwise, a ValueError is thrown
        """
        if node.parents or node.children:
            raise ValueError('The node is not allowed to have any edges')
        self.__nodes[node.node_id] = node
        return node

    def remove_node(self, node: Node):
        """
        removes the given node and all its edges
        """
        for parent in list(node.parents):
            self.remove_edge(Edge(parent, node))
        for child in list(node.children):
            self.remove_edge(Edge(node, child))
        self.__nodes.pop(node.node_id)

    def add_edge(self, from_node: Node, to_node: Node) -> Edge:
        """
        adds a new edge with the given from and to

        Parameters
        ----------
        from_node : Node
            the source node of the edge.
        from_node : Node
            the target node of the edge.

        Returns
        -------
        Node
            the created edge
        """
        if to_node == self.source:
            raise ValueError('connections to the source node are not allowed')
        if from_node == self.sink:
            raise ValueError('connections from the sink node are not allowed')
        edge = Edge(from_node, to_node)
        from_node.children.add(to_node)
        to_node.parents.add(from_node)
        self.__edges[(edge.from_node, edge.to_node)] = edge
        return edge

    def add_removed_edge(self, edge: Edge):
        """
        re-adds an edge that formerly has been removed
        """
        edge.from_node.children.add(edge.to_node)
        edge.to_node.parents.add(edge.from_node)
        self.__edges[(edge.from_node, edge.to_node)] = edge

    def remove_edge(self, edge: Edge):
        """
        removes the given edge from this graph
        """
        edge.from_node.children.remove(edge.to_node)
        edge.to_node.parents.remove(edge.from_node)
        self.__edges.pop((edge.from_node, edge.to_node))

    def nodes(self) -> Generator[Node,None,None]:
        """
        enables iteration over the nodes in this graph. source and sink are
        excluded.
        """
        for node in self.__nodes.values():
            yield node

    def iterate_bfs(self) -> Generator[Node,None,None]:
        """
        enables iteration over nodes in this graph in BFS order starting at source.
        source and sink are included in the result. if there are cycles in the graph,
        this method will stay in an infinite loop
        """
        open_nodes = deque()
        open_nodes.append(self.source)
        while open_nodes:
            node = open_nodes.popleft()
            yield node
            open_nodes.extend(node.children)

    def edges(self) -> Generator[Edge,None,None]:
        """
        enables iteration over the nodes in this graph
        """
        for edge in self.__edges.values():
            yield edge

    def get_edge(self, from_node: Node, to_node: Node) -> Edge:
        """
        retrieves the Edge from "from_node" to "to_node". raises a KeyError if
        there is no such an edge

        Parameters
        ----------
        from_node : Node
            start node of the edge
        to_node : Node
            end node of the edge

        Returns
        -------
        Edge
            if this edge exists in the graph, else a KeyError is thrown
        """
        return self.__edges[(from_node, to_node)]

    def find_shortest_path_to_event(
            self, start_node: Node, target_event: str) -> Union[None, List[Node]]:
        """
        tries to find a path from a start_node to a node with the specified
        event. if there is more than one shortest path, then the first one is
        returned.

        Parameters
        ----------
        start_node : Node
            search starts at this node
        target_event : str
            we want to find the shortest path from the start_node to any node
            with this event

        Returns
        -------
        Union[None, List[None]]
            None if there is no path, otherwise a list of nodes that are
            on the path between start_node and end_node. start_node is the first
            element in the list, the end_node is the last element.
        """
        return self.__find_shortest_path(
            start_node, lambda node: node.event == target_event)

    def find_shortest_paths_to_event(
            self, start_node: Node, target_event: str) -> List[List[Node]]:
        """
        tries to find a path from a start_node to a node with the specified
        event. if there is more than one shortest path, then all paths are
        returned.

        Parameters
        ----------
        start_node : Node
            search starts at this node
        target_event : str
            we want to find the shortest path from the start_node to any node
            with this event

        Returns
        -------
       List[List[Node]]
            empty list if there is no path, otherwise a list of lists of nodes
            that are on the path between start_node and end_node.
            start_node is the first element in each list, the end_node is the
            last element.
        """
        visited = {start_node}
        queue = deque([(start_node, [])])
        found_paths = []

        while queue:
            current_node, path = queue.popleft()
            visited.add(current_node)
            for neighbor in current_node.children:
                if neighbor.event == target_event:
                    end_path = path + [current_node, neighbor]
                    if found_paths and len(end_path) > len(found_paths[-1]):
                        return found_paths
                    found_paths.append(end_path)
                if neighbor not in visited:
                    queue.append((neighbor, path + [current_node]))
                    visited.add(neighbor)

        return found_paths

    def find_shortest_path(
            self, start_node: Node, end_node: Node) -> Union[None, List[None]]:
        """
        tries to find a path from a start_node to an end_node

        Parameters
        ----------
        start_node : Node
            search starts at this node
        end_node : Node
            this is the target node. we want to find a from the start_node to
            this end_node

        Returns
        -------
        Union[None, List[None]]
            None if there is no path, otherwise a list of nodes that are
            on the path between start_node and end_node. start_node is the first
            element in the list, the end_node is the last element.
        """
        return self.__find_shortest_path(
            start_node, lambda node: node.node_id == end_node.node_id)

    def __find_shortest_path(self, start_node: Node, target_found: Callable[[Node], bool]):
        visited = {start_node}
        queue = deque([(start_node, [])])

        while queue:
            current_node, path = queue.popleft()
            visited.add(current_node)
            for neighbor in current_node.children:
                if target_found(neighbor):
                    path.extend([current_node, neighbor])
                    return path
                if neighbor not in visited:
                    queue.append((neighbor, path + [current_node]))
                    visited.add(neighbor)

        # no path found
        return None

    def find_chains(self, min_length: int = 2) -> Generator[List[Node], None, None]:
        """
        yields chains (sequences) of nodes in the graph

        Parameters
        ----------
        min_length : int, optional
            minimal number of nodes that muse be in the chain. shorter chains
            are filtered our. default is 2.

        Yields
        -------
        Generator[Tuple[Node], None, None]
        """
        for node in itertools.chain(self.nodes(), [self.source]):
            #find all nodes that are potential beginnings of a chain
            if len(node.children) == 1 and (
                    len(node.parents) != 1 or len(next(iter(node.parents)).children) > 1):
                sequence = self.__find_chain(node)
                if len(sequence) >= min_length:
                    yield sequence

    def __find_chain(self, node: Node) -> List[Node]:
        chain = [node]
        node = next(iter(node.children))
        while len(node.parents) == 1:
            chain.append(node)
            if len(node.children) != 1:
                break
            node = next(iter(node.children))
        return chain

    def find_chain_containing_node(self, node: Node) -> List[Node]:
        """
        returns a list of nodes with the following properties:
        1. the list has length >= 1 and contains the given node
        2. there is an edge from result[i] to result[i+1]
        3. only result[0] is allowed to have ingoing edges from nodes
           not contained in the chain
        4. only result[-1] is allowed to have outgoing edges to nodes not
           contained in the chain
        """
        start_node = node
        while len(start_node.parents) == 1:
            start_node = next(iter(start_node.parents))
        return self.__find_chain(start_node)

    def compute_mdl(self, event_alphabet: Set[str]) -> float:
        """
        computes the minimum-description-length of this graph. the MDL is a
        surrogate for the model complexity and is an approximation of the
        Kolmogorov complexity of this graph.

        Parameters
        ----------
        event_aphabet : Set[str]
            the set of events in the alphabet, i.e. which the set of events
            that can be used to construct nodes in the graph

        Returns
        -------
        float
            the MDL of this graph
        """
        #encode nr of nodes (can be 0)
        mdl = mdl_utils.L_N(self.get_nr_of_nodes() + 1)
        #encode event of each node
        mdl += self.get_nr_of_nodes() * log2(len(event_alphabet))
        #encode nr of edges
        #max_nr_of_edges = 0.5 * (self.get_nr_of_nodes()+2) * (self.get_nr_of_nodes()+1)
        max_nr_of_edges = (self.get_nr_of_nodes()+1)**2
        mdl += log2(max_nr_of_edges + 1)
        mdl += mdl_utils.log2binom(max_nr_of_edges, self.get_nr_of_edges())
        return  mdl

    def plot(self, show: bool = True, filepath: str = None,
             with_node_ids: bool = False,
             edge_weight_attribute: Union[str, None] = None,
             edge_label_attribute: Union[str, None] = None,
             min_pen_width: float = 1.0,
             max_pen_width: float = 10.0) -> str:
        """
        plots this graph and returns the graphviz DOT code

        Parameters
        ----------
        show : bool, optional
            if True, the graph will be shown immediately, by default True
        filepath : str, optional
            if not None, the plot will be stored to a file, by default None
        with_node_ids : bool, optional
            if True, the nodes will contain "node_id | event",
            otherwise, only the event will be printed.
            by default False
        edge_weight_attribute : Union[str, None], optional
            an edge attribute name that is used to draw the weight of the edge
        edge_label_attribute : Union[str, None], optional
            an edge attribute name that is used to add a label on the edge
        min_pen_width : float, optional
            minimum pen width to draw edges. default is 1.0
        max_pen_width : float, optional
            maximum pen width to draw edges. default is 5.0

        Returns
        -------
        str
            the graphviz dot code
        """
        graph = Digraph()

        for node in itertools.chain(self.nodes(), [self.source, self.sink]):
            node_text = node.event
            if with_node_ids:
                node_text = str(node.node_id) + ' | ' + node.event
            graph.node(str(node.node_id), label=node_text)

        min_edge_weight = float('inf')
        max_edge_weight = float('-inf')
        if edge_weight_attribute is not None:
            for edge in self.edges():
                min_edge_weight = min(min_edge_weight, edge.attributes[edge_weight_attribute])
                max_edge_weight = max(max_edge_weight, edge.attributes[edge_weight_attribute])

        for edge in self.edges():
            edge_attributes = {}
            if edge_label_attribute is not None:
                edge_attributes['label'] = str(edge.attributes[edge_label_attribute])
            if edge_weight_attribute is not None:
                relative_pen_width = (edge.attributes[edge_weight_attribute] -
                                      min_edge_weight) / max_edge_weight
                edge_attributes['penwidth'] = str(
                    min_pen_width + (max_pen_width - min_pen_width) * relative_pen_width)

            graph.edge(str(edge.from_node.node_id), str(edge.to_node.node_id),
                       **edge_attributes)

        return gviz_utils.plot_graph(graph, view=show, filepath=filepath)

    def contains_cycle(self) -> bool:
        """
        returns True iff there is a cycle in this graph
        """
        graph = nx.DiGraph((edge.from_node.node_id, edge.to_node.node_id)
                           for edge in self.edges())

        try:
            next(nx.simple_cycles(graph))
            return True
        except StopIteration:
            return False

    def to_networkx(self) -> nx.DiGraph:
        """
        creates a networkx representation of this graph. the events of the nodes
        are stored in the "event" attribute of the networkx nodes.

        Returns
        -------
        nx.DiGraph
        """
        graph = nx.DiGraph((edge.from_node.node_id, edge.to_node.node_id)
                           for edge in self.edges())
        for node in itertools.chain(self.nodes(), [self.source, self.sink]):
            graph.nodes[node.node_id]['event'] = node.event
        return graph

    def to_json(self) -> str:
        """
        creates a JSON representation of this graph

        Returns
        -------
        str
            a JSON representation of this graph
        """
        dictionary = {}

        dictionary['nodes'] = [
            {
                'node_id': node.node_id,
                'event': node.event,
                'attributes': node.attributes
            }
            for node in self.nodes()
        ]

        dictionary['edges'] = [
            {
                'from_node_id': edge.from_node.node_id,
                'to_node_id': edge.to_node.node_id
            }
            for edge in self.edges()
        ]

        return json.dumps(dictionary)

    @staticmethod
    def from_json(json_string: str) -> 'EventFlowGraph':
        graph = EventFlowGraph()
        dictionary = json.loads(json_string)

        node_id_to_node = {
            graph.source.node_id: graph.source,
            graph.sink.node_id: graph.sink
        }

        for node_dict in dictionary['nodes']:
            node = Node(node_dict['node_id'], node_dict['event'])
            node.attributes = node_dict['attributes']
            graph.add_removed_node(node)
            node_id_to_node[node.node_id] = node

        for edge_dict in dictionary['edges']:
            graph.add_edge(
                node_id_to_node[edge_dict['from_node_id']],
                node_id_to_node[edge_dict['to_node_id']]
            )

        return graph

    @staticmethod
    def chains_have_common_event(chain_a: List[Node], chain_b: List[Node]) -> bool:
        """
        returns True iff chain_a contains a node with an event that is the same
        event as the event of any node in chain_b
        """
        events_in_a = set(node.event for node in chain_a)
        for node in chain_b:
            if node.event in events_in_a:
                return True
        return False

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        if not isinstance(other, EventFlowGraph):
            return False
        return (self.__nodes == other.__nodes and self.__edges == other.__edges)

    def __repr__(self) -> str:
        return self.to_json()

    def copy(self) -> 'EventFlowGraph':
        """
        returns a deep copy of this eventflow graph
        """
        return EventFlowGraph.from_json(self.to_json())

    def merge_redundant_nodes(self):
        """
        merges nodes that have the same label and have an identical
        set of parents or an identical set of children
        """
        self.__merge_nodes_with_same_label_and_parents()
        self.__merge_nodes_with_same_label_and_children()

    def __merge_nodes_with_same_label_and_parents(self):
        candidates = set(self.nodes())
        candidates.add(self.source)

        while candidates:
            parent = candidates.pop()
            grouped_children = defaultdict(list)
            for child in parent.children:
                grouped_children[(frozenset(child.parents), child.event)].append(child)
            for child_group in grouped_children.values():
                if len(child_group) > 1:
                    merged_node = self.__merge_nodes(child_group)
                    candidates.add(merged_node)

    def __merge_nodes_with_same_label_and_children(self):
        candidates = set(self.nodes())
        candidates.add(self.source)

        while candidates:
            child = candidates.pop()
            grouped_parents = defaultdict(list)
            for parent in child.parents:
                grouped_parents[(frozenset(parent.children), parent.event)].append(parent)
            for parent_group in grouped_parents.values():
                if len(parent_group) > 1:
                    merged_node = self.__merge_nodes(parent_group)
                    candidates.add(merged_node)

    def __merge_nodes(self, node_list: List[Node]) -> Node:
        merged_node = node_list[0]
        for redundant_node in node_list[1:]:
            for parent in redundant_node.parents:
                self.add_edge(parent, merged_node)
            for child in redundant_node.children:
                self.add_edge(merged_node, child)
            self.remove_node(redundant_node)
        return merged_node

    def remove_edges_without_instances(self):
        """
        removes all edges with edge.attributes['nr_of_instances'] == 0
        also removes all nodes without any parents (except self.source)
        """
        for edge in list(self.edges()):
            if edge.attributes['nr_of_instances'] == 0:
                self.remove_edge(edge)

        for node in list(self.nodes()):
            if len(node.parents) == 0:
                self.remove_node(node)

    def remove_illegal_source_nodes(self):
        """
        removes all nodes that have no parents. then repeats this for the
        children of the removed nodes that now have no parents.
        """
        nodes_to_remove = [node for node in self.nodes() if len(node.parents) == 0]
        while nodes_to_remove:
            node = nodes_to_remove.pop()
            for child in node.children:
                if len(child.parents) == 1:
                    nodes_to_remove.append(child)
            self.remove_node(node)
