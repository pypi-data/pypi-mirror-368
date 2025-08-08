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
"""
transforms a TargetSequenceDataset to a ClassificationDataset and stores the
mapping between classes and sequences
"""

from typing import Tuple, Dict

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.models.dataset import ClassificationDataset
from prolothar_common.models.dataset.instance import ClassificationInstance

class SequenceToClassDatasetConverter():
    """
    transforms a TargetSequenceDataset to a ClassificationDataset and stores the
    mapping between classes and sequences
    """

    def __init__(self, dataset: TargetSequenceDataset):
        self.__converted_dataset = ClassificationDataset(
            dataset.get_categorical_attribute_names(),
            dataset.get_numerical_attribute_names()
        )

        self.__sequence_to_class = {}

        for instance in dataset:
            class_label = self.__sequence_to_class.get(instance.get_target_sequence(), None)
            if class_label is None:
                class_label = str(len(self.__sequence_to_class))
                self.__sequence_to_class[instance.get_target_sequence()] = class_label

            self.__converted_dataset.add_instance(ClassificationInstance(
                instance.get_id(),
                instance.get_features_dict(),
                class_label
            ))

        self.__class_to_sequence = {v: k for k,v in self.__sequence_to_class.items()}

    def get_converted_dataset(self) -> ClassificationDataset:
        return self.__converted_dataset

    def get_class_to_sequence_mapping(self) -> Dict[str, Tuple[str]]:
        return self.__class_to_sequence

    def get_sequence(self, class_label: str) -> Tuple[str]:
        return self.__class_to_sequence[class_label]