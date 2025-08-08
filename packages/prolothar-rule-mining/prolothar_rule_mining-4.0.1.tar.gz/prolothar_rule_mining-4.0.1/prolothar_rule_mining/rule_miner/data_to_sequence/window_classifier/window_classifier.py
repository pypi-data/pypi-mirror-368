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
from itertools import chain

from prolothar_common.func_tools import do_nothing

from prolothar_common.models.dataset import TargetSequenceDataset, ClassificationDataset
from prolothar_common.models.dataset.instance import ClassificationInstance

from prolothar_rule_mining.rule_miner.classification.rce import ReliableRuleMiner

from prolothar_rule_mining.rule_miner.data_to_sequence.rules import Rule
from prolothar_rule_mining.rule_miner.data_to_sequence.window_classifier.window_rule import WindowRule
from prolothar_rule_mining.rule_miner.data_to_sequence.window_classifier.window_rule import ATTRIBUTE_SEQUENCE_LENGTH

class WindowClassifier():
    """
    learns to predict the next event from the features + a window of the last n events.
    """

    def __init__(self, nr_of_past_events_as_features: int = 3, classification_rule_miner = None):
        self.__past_events_feature_names = [
            f'past_event_{i+1}' for i in range(nr_of_past_events_as_features)]
        if classification_rule_miner is not None:
            self.__classification_rule_miner = classification_rule_miner
        else:
            self.__classification_rule_miner = ReliableRuleMiner(logger=do_nothing)

    def mine_rules(self, dataset: TargetSequenceDataset) -> Rule:
        classification_dataset = self.__build_classification_dataset(dataset)
        return WindowRule(
            self.__past_events_feature_names,
            self.__classification_rule_miner.mine_rules(classification_dataset),
            max(len(instance.get_target_sequence()) for instance in dataset))

    def __build_classification_dataset(self, dataset: TargetSequenceDataset) -> ClassificationDataset:
        classification_dataset = ClassificationDataset(
            dataset.get_categorical_attribute_names() + self.__past_events_feature_names,
            dataset.get_numerical_attribute_names() + [ATTRIBUTE_SEQUENCE_LENGTH],
        )

        for instance in dataset:
            for i, event in enumerate(chain(instance.get_target_sequence(), [''])):
                attributes = dict(instance.get_features_dict())
                for j, feature_name in enumerate(self.__past_events_feature_names):
                    try:
                        attributes[feature_name] = instance.get_target_sequence()[i-j-1]
                    except IndexError:
                        attributes[feature_name] = ''
                attributes[ATTRIBUTE_SEQUENCE_LENGTH] = i
                classification_dataset.add_instance(ClassificationInstance(
                    f'{instance.get_id()}_{i}', attributes, event
                ))

        return classification_dataset
