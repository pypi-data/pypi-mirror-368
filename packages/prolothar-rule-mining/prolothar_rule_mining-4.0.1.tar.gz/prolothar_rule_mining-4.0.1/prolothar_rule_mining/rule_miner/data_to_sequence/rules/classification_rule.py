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
from typing import Dict, Tuple

from prolothar_rule_mining.rule_miner.classification.rules import Rule

class ClassificationRule():
    """
    a data to sequence rule interface that is based on learned classifactor that
    predicts a class label which corresponds to a sequence in the training set
    """

    def __init__(self, classification_rule: Rule, class_to_sequence: Dict[str, Tuple[str]]):
        self.__classification_rule = classification_rule
        self.__class_to_sequence = class_to_sequence

    def execute(self, instance) -> Tuple[str]:
        """generates a sequence for the given instance as input"""
        return self.__class_to_sequence[self.__classification_rule.predict(instance)]

    def count_nr_of_terms(self) -> int:
        """
        returns the number of terms (atomic conditions).
        "If a > 2 and b <= 3 then append(x)" returns 2
        """
        return self.__classification_rule.count_nr_of_terms()
