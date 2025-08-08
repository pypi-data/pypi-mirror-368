from typing import Set

from prolothar_rule_mining.rule_miner.multilabel.rules.rule import Rule

from prolothar_common.models.dataset.instance import Instance

class OutputFixedSetRule(Rule):
    """
    multilabel classification rule that always predicts the same fixed set
    of labgels
    """

    def __init__(self, output: Set[str]):
        self.__output = output

    def predict(self, instance: Instance) -> Set[str]:
        return self.__output

    def to_string(self, prefix='') -> str:
        return prefix + str(self.__output)

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return self.to_string()

    def __hash__(self) -> int:
        return hash(self.to_string())
