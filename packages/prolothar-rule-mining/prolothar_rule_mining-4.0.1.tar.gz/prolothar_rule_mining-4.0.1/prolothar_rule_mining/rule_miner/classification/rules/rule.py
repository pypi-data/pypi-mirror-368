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
from abc import ABC, abstractmethod

from prolothar_common.models.dataset.instance import Instance

class Rule(ABC):
    """interface of a classification rule"""

    @abstractmethod
    def predict(self, instance: Instance) -> str:
        """predicts a class for the given instance as input"""

    @abstractmethod
    def to_string(self, prefix='') -> str:
        """returns a human readable string representation of this rule
        Args:
            prefix:
                can be used for indentation
        """

    @abstractmethod
    def to_html(self) -> str:
        """returns a human readable html string representation of this rule"""

    @abstractmethod
    def get_set_of_output_classes(self) -> Set[str]:
        """
        returns the set of classes this rule can return during predict()
        """

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return self.to_string()

    def __hash__(self) -> int:
        return hash(self.to_string())
