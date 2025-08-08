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
from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_rule_mining.models.converter.sequence_to_class_dataset_converter import SequenceToClassDatasetConverter

from prolothar_rule_mining.rule_miner.data_to_sequence.rules import Rule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules import ClassificationRule

class ClassificationMiner():
    """
    reduces the sequence prediction task to a classification task, i.e. each
    unique sequence in the dataset corresponds to one class
    """

    def __init__(self, classification_miner):
        self.__classification_miner = classification_miner

    def mine_rules(self, dataset: TargetSequenceDataset) -> Rule:
        sequence_to_class_converter = SequenceToClassDatasetConverter(dataset)
        classification_rule = self.__classification_miner.mine_rules(
            sequence_to_class_converter.get_converted_dataset())
        return ClassificationRule(
            classification_rule,
            sequence_to_class_converter.get_class_to_sequence_mapping())