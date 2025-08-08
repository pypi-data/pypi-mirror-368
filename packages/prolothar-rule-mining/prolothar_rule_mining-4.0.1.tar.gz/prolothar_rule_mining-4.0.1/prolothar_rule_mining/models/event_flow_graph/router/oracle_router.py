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
from typing import Dict, Set

from prolothar_common.models.dataset.instance import TargetSequenceInstance
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node
from prolothar_rule_mining.models.event_flow_graph.alignment.petrinet import PetrinetAligner

class GlobalOracleRouter():
    def __init__(self, graph: EventFlowGraph):
        self.__alignment_finder = PetrinetAligner(graph)
        self.__instance_routing_table: Dict[TargetSequenceInstance, Dict[Node, Node]] = {}
        self.__graph = graph

    def decide(self, instance: TargetSequenceInstance, node: Node) -> Node:
        if instance not in self.__instance_routing_table:
            self.__add_instance_to_routing_table(instance)
        return self.__instance_routing_table[instance][node]

    def __add_instance_to_routing_table(self, instance: TargetSequenceInstance):
        current_node = self.__graph.source
        routing_table = {}
        for move in self.__alignment_finder.compute_alignment(instance.get_target_sequence()):
            if move.is_sync_move() or move.is_model_move():
                routing_table[current_node] = move.node
                current_node = move.node
        self.__instance_routing_table[instance] = routing_table

class LocalOracleRouter():
    """
    for evaluation purposes only. this router uses the target sequence of the
    instance to find a route through the graph using the cover algorithm. it thus
    is an upper bound for other routers.
    """
    def __init__(self, global_router: GlobalOracleRouter, node: Node):
        self.__global_router = global_router
        self.__node = node

    def __call__(self, instance: TargetSequenceInstance) -> Node:
        return self.__global_router.decide(instance, self.__node)

    def get_set_of_output_nodes(self) -> Set[Node]:
        return set(self.__node.children)
