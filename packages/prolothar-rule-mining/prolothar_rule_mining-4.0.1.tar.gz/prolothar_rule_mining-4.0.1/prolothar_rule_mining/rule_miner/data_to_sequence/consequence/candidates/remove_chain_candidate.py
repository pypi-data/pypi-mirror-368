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
from typing import List, Union, Set, Generator

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node
from prolothar_rule_mining.models.event_flow_graph.cover import Cover

from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates.candidate import Candidate
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates.not_applicable_error import NotApplicableError

class RemoveChainCandidate(Candidate):
    """
    candidate that removes a list nodes from the EventFlowGraph
    """

    def __init__(
            self, graph: EventFlowGraph, nodes: List[Node]):
        if len(nodes) == 1:
            frequency = sum(
                graph.get_edge(parent, nodes[0]).attributes['nr_of_instances']
                for parent in nodes[0].parents
            )
        else:
            frequency = graph.get_edge(nodes[0], nodes[1]).attributes['nr_of_instances']
        super().__init__(graph, (frequency,))
        self.__nodes = nodes
        self.__parents_of_chain: Union[Set[Node], None] = None
        self.__children_of_chain: Union[Set[Node], None] = None
        self.__sink = graph.sink
        self.__source = graph.source
        self._g = graph

    def _apply(self):
        self.__assert_still_applicable()
        self.__parents_of_chain = set(self.__nodes[0].parents)
        self.__children_of_chain = set(self.__nodes[-1].children)
        if self.__nodes[0] is self.__source and self.__nodes[-1] is self.__sink:
            last_node = self.__nodes[0]
            for node in self.__nodes[1:]:
                self._remove_edge(last_node, node)
                last_node = node
            for node in self.__nodes[1:-1]:
                self._remove_node(node)
            self._add_edge(self.__source, self.__sink)
        else:
            for node in self.__nodes:
                for parent in list(node.parents):
                    self._remove_edge(parent, node)
                for child in list(node.children):
                    self._remove_edge(node, child)
                self._remove_node(node)

    def __assert_still_applicable(self):
        #all nodes must be in the graph
        for node in self.__nodes:
            if not self._graph_contains_node(node):
                raise NotApplicableError()
        #except of the start node, all nodes must have one parent to be in a chain
        for node in self.__nodes[1:]:
            if len(node.parents) != 1:
                raise NotApplicableError()
        #except of the end node, all nodes must have one child to be in chain
        for node in self.__nodes[:-1]:
            if len(node.children) != 1:
                raise NotApplicableError()
        #make sure that the start node is really the beginning of the chain
        if len(self.__nodes[0].parents) == 1:
            parent = next(iter(self.__nodes[0].parents))
            if len(parent.children) == 1:
                raise NotApplicableError()
        #make sure that the end node is really the end of the chain
        if len(self.__nodes[-1].children) == 1:
            child = next(iter(self.__nodes[-1].children))
            if len(child.parents) == 1:
                raise NotApplicableError()
        #make sure that no dead ends are created, except source to sink
        for parent in self.__nodes[0].parents:
            if len(parent.children) == 1 and parent is not self.__source:
                raise NotApplicableError()
        #chain that starts with source xor sink is invalid
        if self.__nodes[0] is self.__source != self.__nodes[-1] is self.__sink:
            raise NotApplicableError()

    def post_process_cover_after_apply(self, cover: Cover):
        for node in self.get_removed_nodes():
            cover.model_codes.pop(node, None)
            cover.missed_event_codes.pop(node, None)
            cover.matched_event_codes.pop(node, None)
            cover.redundant_event_codes.pop(node, None)

    def yield_new_candidates(
            self, graph: EventFlowGraph) -> Generator[Candidate, None, None]:
        locked_nodes = set()
        for parent in self.__parents_of_chain:
            if len(parent.children) == 1:
                chain = graph.find_chain_containing_node(parent)
                locked_nodes.update(chain)
                yield RemoveChainCandidate(graph, chain)
        for child in self.__children_of_chain:
            if child not in locked_nodes and len(child.parents) == 1:
                chain = graph.find_chain_containing_node(child)
                yield RemoveChainCandidate(graph, chain)

    def leads_to_cycle(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'RemoveChainCandidate(%r)' % self.__nodes
