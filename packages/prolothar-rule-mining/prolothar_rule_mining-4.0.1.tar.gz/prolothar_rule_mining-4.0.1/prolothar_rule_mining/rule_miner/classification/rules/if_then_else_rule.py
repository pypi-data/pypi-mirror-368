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

from prolothar_rule_mining.rule_miner.classification.rules.rule import Rule
from prolothar_rule_mining.rule_miner.classification.rules.list_of_rules import ListOfRules
from prolothar_rule_mining.models.conditions import Condition

class IfThenElseRule(Rule):
    """rule with an if and an else branch"""
    def __init__(self, condition: Condition, if_branch: ListOfRules = None,
                 else_branch: ListOfRules = None):
        self.__condition = condition
        if if_branch is None:
            self.__if_branch = ListOfRules()
        else:
            self.__if_branch = if_branch
        if else_branch is None:
            self.__else_branch = ListOfRules()
        else:
            self.__else_branch = else_branch

    def predict(self, instance: Instance) -> str:
        if self.__condition.check_instance(instance):
            return self.__if_branch.predict(instance)
        else:
            return self.__else_branch.predict(instance)

    def __eq__(self, other) -> bool:
        try:
            return (self.__condition == other.__condition and
                    self.__if_branch == other.__if_branch and
                    self.__else_branch == other.__else_branch)
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return hash((self.__condition, self.__if_branch, self.__else_branch))

    def get_if_branch(self) -> ListOfRules:
        return self.__if_branch

    def get_else_branch(self) -> ListOfRules:
        return self.__else_branch

    def set_condition(self, condition: Condition):
        self.__condition = condition

    def get_condition(self) -> Condition:
        return self.__condition

    def count_nr_of_terms(self) -> int:
        nr_of_terms = self.__condition.count_nr_of_terms()
        nr_of_terms += self.__if_branch.count_nr_of_terms()
        nr_of_terms += self.__else_branch.count_nr_of_terms()
        return nr_of_terms

    def to_string(self, prefix='') -> str:
        s = '%sIF %s THEN\n%s' % (prefix, str(self.__condition),
                                self.__if_branch.to_string(prefix + '  '))
        if len(self.__else_branch) > 0:
            s += '\n%sELSE\n%s' % (prefix,
                                   self.__else_branch.to_string(prefix + '  '))
        return s

    def to_html(self) -> str:
        return ('<div class="Rule IfThenElseRule">'
                '<div class="If">If</div>'
                '%s'
                '<div class="ifbranch">%s</div>'
                '%s'
                '<div class="elsebranch">%s</div>'
                '</div>') % (
                    self.__condition.to_html(),
                    self.__if_branch.to_html(),
                    '<div class="Else">Else</div>' if len(self.__else_branch) > 0 else '',
                    self.__else_branch.to_html()
                )

    def contains_symbol(self, symbol: str) -> bool:
        return (self.__if_branch.contains_symbol(symbol) or
                self.__else_branch.contains_symbol(symbol))

    def get_set_of_output_classes(self) -> Set[str]:
        classes = self.__if_branch.get_set_of_output_classes()
        classes.update(self.__else_branch.get_set_of_output_classes())
        return classes
