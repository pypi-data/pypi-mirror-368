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
from prolothar_common.models.dataset import Dataset, ClassificationDataset
from prolothar_common.models.dataset.instance import ClassificationInstance
from prolothar_rule_mining.rule_miner.classification.rules import ReturnClassRule
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph import Node
from prolothar_rule_mining.models.event_flow_graph.router.router import Router
from prolothar_rule_mining.models.event_flow_graph.router.ruled_router import RuledRouter

class RuleClassifierRouterLearner():

    def __init__(self, rule_miner):
        """
        Parameters
        ----------
        rule_miner
            a classification rule miner
        """
        self.__rule_miner = rule_miner

    def __call__(self, node: Node, event_flow_graph: EventFlowGraph,
                 dataset: Dataset) -> Router:
        decision_dataset = ClassificationDataset(
            categorical_attribute_names=dataset.get_categorical_attribute_names(),
            numerical_attribute_names=dataset.get_numerical_attribute_names())
        for child in node.children:
            for instance in event_flow_graph.get_edge(node, child).attributes['instances']:
                decision_dataset.add_instance(ClassificationInstance(
                    instance.get_id(), instance.get_features_dict(), str(child.node_id)
                ))

        if len(decision_dataset.get_set_of_classes()) == 1:
            rule = ReturnClassRule(next(iter(decision_dataset.get_set_of_classes())))
        elif not decision_dataset.get_set_of_classes():
            rule = ReturnClassRule(str(next(iter(node.children)).node_id))
        else:
            rule = self.__rule_miner.mine_rules(decision_dataset)

        return RuledRouter(
            {child.node_id: child for child in node.children},
            rule
        )

    def __repr__(self) -> str:
        return 'RuleClassifierRouterLearner(%r)' % self.__rule_miner
