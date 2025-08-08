from typing import Set

from abc import ABC, abstractmethod

from prolothar_common.models.dataset.instance import Instance

class Rule(ABC):
    """interface of a multilabel classification rule"""

    @abstractmethod
    def predict(self, instance: Instance) -> Set[str]:
        """predicts a set of class label for the given instance as input"""

    @abstractmethod
    def to_string(self, prefix='') -> str:
        """returns a human readable string representation of this rule
        Args:
            prefix:
                can be used for indentation
        """

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return self.to_string()

    def __hash__(self) -> int:
        return hash(self.to_string())
