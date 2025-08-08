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

from prolothar_common.models.dataset.instance import Instance
from prolothar_rule_mining.models.event_flow_graph import Node
from prolothar_rule_mining.rule_miner.classification.rules import Rule

class RuledRouter():

    def __init__(self, node_id_to_node: Dict[int, Node], rule: Rule):
        self.__node_id_to_node = node_id_to_node
        self.__rule = rule

    def __call__(self, instance: Instance) -> Node:
        try:
            return self.__node_id_to_node[int(self.__rule.predict(instance))]
        except Exception as e:
            raise NotImplementedError(self.__rule)

    def get_rule(self) -> Rule:
        return self.__rule

    def get_set_of_output_nodes(self) -> Set[Node]:
        return set(
            self.__node_id_to_node[int(node_id)]
            for node_id in self.__rule.get_set_of_output_classes())