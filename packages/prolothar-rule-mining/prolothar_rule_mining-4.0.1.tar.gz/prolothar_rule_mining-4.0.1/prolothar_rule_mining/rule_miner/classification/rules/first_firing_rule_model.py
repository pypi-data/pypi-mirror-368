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
from typing import Set

from prolothar_common.models.dataset.instance import Instance

from prolothar_rule_mining.rule_miner.classification.rules.class_output_exception import ClassOutputException
from prolothar_rule_mining.rule_miner.classification.rules.rule import Rule
from prolothar_rule_mining.rule_miner.classification.rules.list_of_rules import ListOfRules

class FirstFiringRuleModel(Rule):
    """
    wrapper for rules that raise ClassOutputException
    """

    def __init__(self, rule: ListOfRules):
        self.__rule = rule

    def predict(self, instance: Instance) -> str:
        try:
            self.__rule.predict(instance)
        except ClassOutputException as e:
            return e.class_label

    def __eq__(self, other) -> bool:
        try:
            return self.__rule == other.__rule
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return hash(self.__rule)

    def to_string(self, prefix='') -> str:
        return self.__rule.to_string(prefix=prefix)

    def to_html(self) -> str:
        return self.__rule.to_html()

    def count_nr_of_terms(self) -> int:
        return self.__rule.count_nr_of_terms()

    def get_rule(self) -> ListOfRules:
        return self.__rule

    def remove_rules_containing_symbol(self, symbol: str):
        self.__rule = ListOfRules([
            subrule for subrule in self.__rule
            if not subrule.contains_symbol(symbol)
        ])

    def get_set_of_output_classes(self) -> Set[str]:
        return self.__rule.get_set_of_output_classes()