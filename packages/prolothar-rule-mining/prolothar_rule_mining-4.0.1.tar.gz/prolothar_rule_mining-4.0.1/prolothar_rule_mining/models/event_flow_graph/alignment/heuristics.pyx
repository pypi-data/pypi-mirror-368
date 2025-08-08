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
from typing import List, Callable, Dict, Set

from collections import deque, defaultdict
import itertools
import networkx as nx

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node
from prolothar_rule_mining.models.event_flow_graph.caching import CachedShortestPathToEventFinder

Heuristic = Callable[[Node, int, List[str]], int]

class NullHeuristic:
    """
    Heuristic that always outputs 0 (i.e. A* star reduces to Dijkstra)
    """
    def __call__(self, node: Node, event_index: int, sequence: Tuple[str]) -> int:
        return 0

class ReachabilityHeuristic:
    """
    for each remaining event in the sequence add +1 to the heuristic value
    if the event is not reachable from the current node
    """
    def __init__(self, graph: EventFlowGraph):
        self.__shortest_path_finder = CachedShortestPathToEventFinder(graph)
        self.__graph = graph

        self.__reachability_table: Dict[Node, Set[str]] = { graph.sink: set() }
        open_nodes = deque(parent for parent in graph.sink.parents if len(parent.children) == 1)
        while open_nodes:
            node = open_nodes.pop()
            reachable_events = set()
            for child in node.children:
                reachable_events.update(self.__reachability_table[child])
                reachable_events.add(child.event)
            self.__reachability_table[node] = reachable_events
            for parent in node.parents:
                if parent not in self.__reachability_table \
                and not parent.children.difference(self.__reachability_table.keys()):
                    open_nodes.appendleft(parent)

    def __call__(self, node: Node, event_index: int, sequence: Tuple[str]) -> int:
        #end of sequence reached, only model moves possible
        cdef int heuristic = 0
        if event_index > len(sequence):
            if node is not self.__graph.sink:
                return len(self.__shortest_path_finder(node, self.__graph.sink.event))
            return 0
        #end of model reached, only log moves possible
        elif node is self.__graph.sink:
            return len(sequence) + 1 - event_index
        else:
            events_reachable_by_node = self.__reachability_table[node]
            for event in sequence[event_index:]:
                if event not in events_reachable_by_node:
                    heuristic += 1
            return heuristic

class ProductNetHeuristic:
    def __init__(self, graph: EventFlowGraph):
        self.__graph = graph.to_networkx()
        self.__shortest_path_finder = CachedShortestPathToEventFinder(graph)
        self.__source_id = graph.source.node_id
        self.__sink_id = graph.sink.node_id
        self.__sink_event = graph.sink.event
        for _, nbrsdict in self.__graph.adjacency():
            for edge_attributes in nbrsdict.values():
                edge_attributes['weight'] = 1
        self.__event_node_index = defaultdict(list)
        for node in graph.nodes():
            self.__event_node_index[node.event].append(node.node_id)

    def __call__(self, node: Node, event_index: int, sequence: Tuple[str]) -> int:
        if event_index >= len(sequence):
            if node.node_id != self.__sink_id:
                return len(self.__shortest_path_finder(node, self.__sink_event))
            return 0
        #end of model reached, only log moves possible
        elif node.node_id == self.__sink_id:
            return len(sequence) + 1 - event_index
        else:
            product_net = self.__create_product_net(node, sequence[event_index:])
            return nx.algorithms.shortest_paths.weighted.single_source_dijkstra(
                product_net, node.node_id, target=self.__sink_id
            )[0]

    def __create_product_net(self, node: Node, sequence: Tuple[str]) -> nx.DiGraph:
        product_net = self.__graph.copy()
        connected_nodes = set(nx.descendants(product_net, node.node_id))
        connected_nodes.update(nx.ancestors(product_net, node.node_id))
        connected_nodes.add(node.node_id)
        product_net.remove_nodes_from(set(product_net.nodes()).difference(connected_nodes))

        last_event_node = 'e'
        product_net.add_node(last_event_node, event=sequence[0])
        product_net.add_edge(self.__source_id, last_event_node, weight=1)
        event_nodes = [last_event_node]
        for i,event in enumerate(sequence[1:]):
            event_node_id = 'e%d' % i
            product_net.add_node(event_node_id, event=event)
            product_net.add_edge(event_nodes[-1], event_node_id, weight=1)
            event_nodes.append(event_node_id)
        product_net.add_edge(event_nodes[-1], self.__sink_id, weight=1)

        for event_node, event in zip(event_nodes, sequence):
            for model_node in self.__event_node_index[event]:
                if model_node in product_net.nodes:
                    self.__create_sync_node(event_node, model_node, product_net)

        return product_net

    def __create_sync_node(self, event_node: str, model_node: int, product_net: nx.DiGraph):
        sync_node_id = event_node + '_' + str(model_node)
        product_net.add_node(sync_node_id)
        for predecessor in itertools.chain(product_net.predecessors(event_node),
                                           product_net.predecessors(model_node)):
            product_net.add_edge(predecessor, sync_node_id, weight=0)

        for ancestor in itertools.chain(product_net.successors(event_node),
                                        product_net.successors(model_node)):
            ancestor_weight = 0 if self.__sink_id == ancestor else 1
            product_net.add_edge(sync_node_id, ancestor, weight=ancestor_weight)

class ShortestPathToSinkHeuristic:
    """
    if remaining sequence is shorter than the shortest path to the model,
    outputs the difference of lengths between the remaining sequence and
    the shortest path (i.e. nr of necessary model moves). otherwise 0 is returned.
    """
    def __init__(self, graph: EventFlowGraph):
        self.__path_lengths = {graph.sink: 0}
        open_nodes = [graph.sink]
        while open_nodes:
            node = open_nodes.pop()
            for parent in node.parents:
                current_cost = self.__path_lengths.get(parent, float('inf'))
                candidate_cost = self.__path_lengths[node] + 1
                if candidate_cost < current_cost:
                    self.__path_lengths[parent] = candidate_cost
                    open_nodes.append(parent)

    def __call__(self, node: Node, event_index: int, sequence: Tuple[str]) -> int:
        length_of_shortest_path_to_sink = self.__path_lengths[node]
        remaining_sequence_length = len(sequence) + 1 - event_index
        return max(length_of_shortest_path_to_sink - remaining_sequence_length, 0)

class MaximumHeuristic:
    """
    outputs the maximum of other heuristics
    """
    def __init__(self, subheuristics: List[Heuristic]):
        self.__subheuristics = subheuristics

    def __call__(self, node: Node, event_index: int, sequence: Tuple[str]) -> int:
        return max(
            heuristic(node, event_index, sequence)
            for heuristic in self.__subheuristics
        )