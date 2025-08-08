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
from typing import List

from prolothar_common.models.dataset.instance import Instance

from prolothar_rule_mining.rule_miner.classification.rules import Rule

ATTRIBUTE_SEQUENCE_LENGTH = '_sequence_length_'

class WindowRule:

    def __init__(self, past_events_feature_names: List[str], classifier: Rule,
                 max_sequence_length: int):
        self.__past_events_feature_names = past_events_feature_names
        self.__classifier = classifier
        self.__max_sequence_length = max_sequence_length

    def execute(self, instance: Instance) -> List[str]:
        """generates a sequence for the given instance as input"""
        sequence = []
        instance = self.__create_initial_instance(instance)
        while len(sequence) < self.__max_sequence_length:
            next_event = self.__classifier.predict(instance)
            if not next_event:
                return sequence
            else:
                sequence.append(next_event)
                instance = self.__prepare_instance_for_next_event_prediction(
                    instance, next_event)
        return sequence

    def __prepare_instance_for_next_event_prediction(
            self, instance: Instance, last_event: str) -> Instance:
        features = instance.get_features_dict()
        for feature_name in self.__past_events_feature_names:
            next_last_event = features[feature_name]
            features[feature_name] = last_event
            last_event = next_last_event
        features[ATTRIBUTE_SEQUENCE_LENGTH] += 1
        return Instance(instance.get_id(), features)

    def __create_initial_instance(self, instance: Instance) -> Instance:
        attributes = dict(instance.get_features_dict())
        for feature_name in self.__past_events_feature_names:
            attributes[feature_name] = ''
        attributes[ATTRIBUTE_SEQUENCE_LENGTH] = 0
        return Instance(instance.get_id(), attributes)

    def count_nr_of_terms(self) -> int:
        """
        returns the number of terms (atomic conditions).
        "If a > 2 and b <= 3 then append(x)" returns 2

        raises an AttributeError if the underlying classifier does not support
        this, i.e. if the classifier is black-box
        """
        return self.__classifier.count_nr_of_terms()

    def __str__(self) -> str:
        return str(self.__classifier)

    def __repr__(self) -> str:
        return repr(self.__classifier)
