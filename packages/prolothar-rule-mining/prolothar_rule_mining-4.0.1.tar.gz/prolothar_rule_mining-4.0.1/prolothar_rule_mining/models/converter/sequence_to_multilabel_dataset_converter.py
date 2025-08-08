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
transforms a TargetSequenceDataset to a MultiLabelDataset, i.e. the sequence
prediction task is transformed to the prediction of occurence (yes/no) of events
"""

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.models.dataset import MultiLabelDataset
from prolothar_common.models.dataset.instance import MultiLabelInstance

class SequenceToMultiLabelDatasetConverter():
    """
    transforms a TargetSequenceDataset to a MultiLabelDataset, i.e. the sequence
    prediction task is transformed to the prediction of occurence (yes/no) of events
    """

    def __init__(self, dataset: TargetSequenceDataset):
        self.__converted_dataset = MultiLabelDataset(
            dataset.get_categorical_attribute_names(),
            dataset.get_numerical_attribute_names()
        )

        for instance in dataset:
            self.__converted_dataset.add_instance(MultiLabelInstance(
                instance.get_id(),
                instance.get_features_dict(),
                set(instance.get_target_sequence())
            ))

    def get_converted_dataset(self) -> MultiLabelDataset:
        return self.__converted_dataset