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
import numpy as np

from prolothar_common.models.dataset import ClassificationDataset

from prolothar_rule_mining.models.conditions import Condition

class CandidateCondition:
    def __init__(self, condition: Condition, class_label: str, causal_effect: float):
        self.condition = condition
        self.class_label = class_label
        self.causal_effect = causal_effect

    def __lt__(self, other: 'CandidateCondition') -> bool:
        return self.causal_effect < other.causal_effect

    def __str__(self) -> str:
        return '%r => %s -- %.3f' % (self.condition, self.class_label, self.causal_effect)

    def __repr__(self) -> str:
        return str(self)

class VectorCandidateCondition(CandidateCondition):
    def __init__(
            self, condition: Condition, condition_hold_vector,
            class_label: str, class_label_hold_vector, causal_effect: float):
        super().__init__(condition, class_label, causal_effect)
        self.condition_hold_vector = condition_hold_vector
        self.class_label_hold_vector = class_label_hold_vector

class LazyVectorCandidateCondition(CandidateCondition):
    def __init__(
            self, condition: Condition, dataset: ClassificationDataset,
            class_label: str, class_label_hold_vector, causal_effect: float):
        super().__init__(condition, class_label, causal_effect)
        self.__dataset = dataset
        self.class_label_hold_vector = class_label_hold_vector
        self.__condition_hold_vector = None

    @property
    def condition_hold_vector(self):
        if self.__condition_hold_vector is None:
            self.__condition_hold_vector = np.array([
                self.condition.check_instance(instance) for instance in self.__dataset
            ], dtype=bool)
        return self.__condition_hold_vector
