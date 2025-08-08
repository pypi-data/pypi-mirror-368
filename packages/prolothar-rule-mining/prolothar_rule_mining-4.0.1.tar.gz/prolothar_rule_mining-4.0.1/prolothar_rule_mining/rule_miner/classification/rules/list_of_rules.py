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
from typing import List, Iterator, Set

from collections import defaultdict

from prolothar_common.models.dataset.instance import Instance
from prolothar_rule_mining.rule_miner.classification.rules.rule import Rule

class ListOfRules(Rule):
    """an ordered list of rules"""
    def __init__(self, rules: List[Rule] = None):
        if rules is None:
            self.__rules: List[Rule] = []
        else:
            self.__rules: List[Rule] = rules

    def __eq__(self, other) -> bool:
        try:
            if len(self) != len(other):
                return False
            for a,b in zip(self.__rules, other.__rules):
                if a != b:
                    return False
            return True
        except AttributeError:
            return False

    def __hash__(self) -> int:
        value = 0
        for rule in self.__rules:
            value = value ^ hash(rule)
        return value

    def predict(self, instance: Instance) -> str:
        votes = defaultdict(int)
        for rule in self.__rules:
            prediction = rule.predict(instance)
            if prediction is not None:
                votes[prediction] += 1
        if votes:
            return max(votes, key = votes.get)

    def append_rule(self, rule: Rule):
        """appends the given rule to the end of this list"""
        self.__rules.append(rule)

    def __len__(self) -> int:
        """returns the number of rules in this list"""
        return len(self.__rules)

    def insert(self, i: int, rule: Rule):
        """insert a rule at the given index"""
        self.__rules.insert(i, rule)

    def remove_index(self, i: int) -> Rule:
        """removes the element at the given index and returns it"""
        return self.__rules.pop(i)

    def __getitem__(self, i: int):
        return self.__rules[i]

    def __setitem__(self, i: int, rule: Rule):
        self.__rules[i] = rule

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.__rules)

    def to_string(self, prefix='') -> str:
        return '\n'.join(rule.to_string(prefix=prefix) for rule in self.__rules)

    def to_html(self) -> str:
        return '<div id="%d" class="Rule ListOfRules">%s</div>' % (
            id(self), ''.join(rule.to_html() for rule in self.__rules))

    def count_nr_of_terms(self) -> int:
        nr_of_terms = 0
        for subrule in self.__rules:
            nr_of_terms += subrule.count_nr_of_terms()
        return nr_of_terms

    def get_list(self) -> List[Rule]:
        return self.__rules

    def contains_symbol(self, symbol: str) -> bool:
        for subrule in self.__rules:
            if subrule.contains_symbol(symbol):
                return True
        return False

    def get_set_of_output_classes(self) -> Set[str]:
        classes = set()
        for rule in self.__rules:
            classes.update(rule.get_set_of_output_classes())
        return classes
