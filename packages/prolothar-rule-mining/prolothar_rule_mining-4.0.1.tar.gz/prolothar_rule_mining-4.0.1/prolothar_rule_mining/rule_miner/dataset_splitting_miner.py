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
from typing import Union, Callable

from prolothar_common.models.dataset import Dataset
from prolothar_rule_mining.rule_miner.classification.rules import Rule as ClassificationRule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules import Rule as DataToSequenceRule
from prolothar_rule_mining.rule_miner.multilabel.rules import Rule as MultilabelRule

Rule = Union[ClassificationRule, DataToSequenceRule, MultilabelRule]

class DatasetSplittingMiner:
    """
    Adapter to use a hold out set training strategy for specific rule miners
    """

    def __init__(
            self, training_function: Callable[[Dataset, Dataset], Rule],
            hold_out_set_ratio: float = 0.2, random_seed: Union[int, None] = None):
        self.__hold_out_set_ratio = hold_out_set_ratio
        self.__random_seed = random_seed
        self.__training_function = training_function

    def mine_rules(self, dataset: Dataset) -> Rule:
        trainset, testset = dataset.split(
            self.__hold_out_set_ratio, random_seed=self.__random_seed)
        return self.__training_function(trainset, testset)
