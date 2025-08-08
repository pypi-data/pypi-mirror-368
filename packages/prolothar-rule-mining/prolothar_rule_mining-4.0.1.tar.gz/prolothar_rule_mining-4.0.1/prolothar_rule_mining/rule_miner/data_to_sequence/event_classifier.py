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
from typing import List, Tuple

from prolothar_common.parallel.abstract.computation_engine import ComputationEngine
from prolothar_common.parallel.single_thread.single_thread import SingleThreadComputationEngine

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.models.dataset import ClassificationDataset
from prolothar_common.models.dataset.instance import ClassificationInstance
from prolothar_common.models.dataset.instance import Instance

from prolothar_rule_mining.rule_miner.data_to_sequence.rules import Rule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules import ClassificationRule

def  _train_classifier(classifier, dataset) -> ClassificationRule:
    return classifier.mine_rules(dataset)

class EventClassifierRule():
    """
    a sequence generation rule that uses classifiers to predict events at each
    possible position of the generated sequence
    """
    def __init__(self, classifier_list: List[ClassificationRule], end_of_sequence_class):
        self.__classifier_list = classifier_list
        self.__end_of_sequence_class = end_of_sequence_class

    def execute(self, instance: Instance) -> Tuple[str]:
        """generates a sequence for the given instance as input"""
        sequence = []
        for classifier in self.__classifier_list:
            predicted_event = classifier.predict(instance)
            if predicted_event == self.__end_of_sequence_class:
                break
            sequence.append(predicted_event)
        return tuple(sequence)

    def count_nr_of_terms(self) -> int:
        """
        returns the number of terms (atomic conditions).
        "If a > 2 and b <= 3 then append(x)" returns 2

        raises an AttributeError if the underlying classifier does not support
        this, i.e. if the classifier is black-box
        """
        return sum(c.count_nr_of_terms() for c in self.__classifier_list)

    def get_classifier_list(self) -> List[ClassificationRule]:
        return self.__classifier_list

    def __repr__(self) -> str:
        return '\n'.join(str(c) for c in self.__classifier_list)

class EventClassifier():
    """
    reduces the sequence prediction task to a classification task where we
    predict the event at each possible position in the sequence
    """

    def __init__(
            self, classification_miner, end_of_sequence_class='_END_',
            computation_engine: ComputationEngine = SingleThreadComputationEngine()):
        self.__classification_miner = classification_miner
        self.__end_of_sequence_class = end_of_sequence_class
        self.__computation_engine = computation_engine

    def mine_rules(self, dataset: TargetSequenceDataset) -> Rule:
        classification_datasets = self.__computation_engine.create_partitionable_list(
            self.__create_classification_datasets(dataset))

        trained_classifiers = list(classification_datasets.map(
                self.__classification_miner, _train_classifier, keep_order=True))

        return EventClassifierRule(trained_classifiers, self.__end_of_sequence_class)

    def __create_classification_datasets(
            self, dataset: TargetSequenceDataset) -> List[ClassificationDataset]:
        max_sequence_length = max(len(instance.get_target_sequence()) for instance in dataset)
        classification_datasets = [
            ClassificationDataset(
                dataset.get_categorical_attribute_names(),
                dataset.get_numerical_attribute_names()
            )
            for _ in range(max_sequence_length)
        ]
        for instance in dataset:
            for i,event in enumerate(instance.get_target_sequence()):
                classification_datasets[i].add_instance(ClassificationInstance(
                    instance.get_id(), instance.get_features_dict(), event
                ))
            for i in range(len(instance.get_target_sequence()), max_sequence_length):
                classification_datasets[i].add_instance(ClassificationInstance(
                    instance.get_id(), instance.get_features_dict(), self.__end_of_sequence_class
                ))
        return classification_datasets
