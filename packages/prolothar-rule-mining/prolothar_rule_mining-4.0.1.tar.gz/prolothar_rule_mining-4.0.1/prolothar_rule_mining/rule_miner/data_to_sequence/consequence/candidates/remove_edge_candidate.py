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

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Edge

from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates.candidate import Candidate
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates.remove_chain_candidate import RemoveChainCandidate
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates.not_applicable_error import NotApplicableError

class RemoveEdgeCandidate(Candidate):
    """
    candidate that removes an edge from the EventFlowGraph
    """

    def __init__(
            self, graph: EventFlowGraph, edge: Edge):
        super().__init__(graph, (edge.attributes['nr_of_instances'],))
        self.__edge = edge

    def _apply(self):
        self.__assert_still_applicable()
        self._remove_edge(self.__edge.from_node, self.__edge.to_node)

    def __assert_still_applicable(self):
        if len(self.__edge.to_node.parents) <= 1 or len(self.__edge.from_node.children) <= 1:
            raise NotApplicableError('edge must not make nodes unreachable')
        if not self._graph_contains_edge(self.__edge):
            raise NotApplicableError('edge must be in graph')

    def yield_new_candidates(
            self, graph: EventFlowGraph) -> Generator[Candidate, None, None]:
        locked_nodes = set()
        if len(self.__edge.from_node.children) == 1:
            chain = graph.find_chain_containing_node(self.__edge.from_node)
            locked_nodes.update(chain)
            yield RemoveChainCandidate(graph, chain)
        if self.__edge.to_node not in locked_nodes and len(self.__edge.to_node.parents) == 1:
            chain = graph.find_chain_containing_node(self.__edge.to_node)
            yield RemoveChainCandidate(graph, chain)

    def leads_to_cycle(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'RemoveEdgeCandidate(%r)' % self.__edge
