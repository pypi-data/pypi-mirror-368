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
from typing import Dict

from prolothar_common.models.dataset import Dataset
from prolothar_common.models.dataset.instance import ClassificationInstance
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph import Node
from prolothar_rule_mining.models.event_flow_graph.router.router import Router
from prolothar_rule_mining.models.event_flow_graph.router.oracle_router import GlobalOracleRouter
from prolothar_rule_mining.models.event_flow_graph.router.oracle_router import LocalOracleRouter

class OracleRouterLearner():

    def __init__(self):
        self.__global_router_dict: Dict[int, GlobalOracleRouter] = {}

    def __call__(self, node: Node, event_flow_graph: EventFlowGraph,
                 dataset: Dataset) -> Router:
        decision_dataset = Dataset(
            categorical_attribute_names=dataset.get_categorical_attribute_names(),
            numerical_attribute_names=dataset.get_numerical_attribute_names())
        for child in node.children:
            for instance in event_flow_graph.get_edge(node, child).attributes['instances']:
                decision_dataset.add_instance(ClassificationInstance(
                    instance.get_id(), instance.get_features_dict(), str(child.node_id)
                ))

        return LocalOracleRouter(self.__get_global_router(event_flow_graph), node)

    def __get_global_router(self, event_flow_graph: EventFlowGraph) -> GlobalOracleRouter:
        graph_id = id(event_flow_graph)
        try:
            return self.__global_router_dict[graph_id]
        except KeyError:
            router = GlobalOracleRouter(event_flow_graph)
            self.__global_router_dict[graph_id] = router
            return router
