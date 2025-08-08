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
from random import Random
from typing import List, Tuple, Union
from abc import ABC, abstractmethod
from frozendict import frozendict

import numpy as np
import lime
import lime.lime_tabular
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.models.dataset.instance import TargetSequenceInstance
from prolothar_common.models.dataset.transformer.one_hot_encoding import OneHotEncoding

from prolothar_rule_mining.rule_miner.data_to_sequence.rules import BlackboxRule

class BaseLstm(BlackboxRule, ABC):

    def __init__(self, train_dataset: TargetSequenceDataset, end_of_sequence_symbol=-1,
                 random_seed: int = None,
                 round_limit: int = None,
                 activation_candidates: List[str] = ['tanh', 'relu', 'elu'],
                 optimizer_candidates: List[str] = ['Adamax', 'Adam', 'Nadam', 'Ftrl'],
                 batch_size_candidates: List[int] = [32, 64, 128, 256],
                 dropout_candidates: List[int] = [0.0, 0.1, 0.2, 0.3, 0.4],
                 layers_candidates: List[Tuple[int]] = [(8,8), (16,16), (32, 32), (64, 64)]):
        if end_of_sequence_symbol in train_dataset.get_set_of_sequence_symbols():
            raise ValueError('end_of_sequence_symbol must not be in symbol set')

        possible_attribute_values = {}
        self.__mean_per_attribute = {}
        self.__stddev_per_attribute = {}
        for attribute in train_dataset.get_attributes():
            if attribute.is_categorical():
                possible_attribute_values[attribute.get_name()] = \
                    attribute.get_unique_values()
            else:
                self.__mean_per_attribute[attribute.get_name()] = np.mean([
                    instance[attribute.get_name()] for instance in train_dataset])
                self.__stddev_per_attribute[attribute.get_name()] = np.std([
                    instance[attribute.get_name()] for instance in train_dataset])
        self.__one_hot_encoder = OneHotEncoding(
            possible_attribute_values=possible_attribute_values)

        self.__max_sequence_length = max(len(instance.get_target_sequence())
                                         for instance in train_dataset) + 1

        self.__sequence_symbol_encoding = {}
        self.__index_sequence_symbol_encoding = {}
        for i,symbol in enumerate(train_dataset.get_set_of_sequence_symbols().union([
                end_of_sequence_symbol])):
            encoded_symbol = [0] * (len(train_dataset.get_set_of_sequence_symbols()) + 1)
            encoded_symbol[i] = 1
            self.__sequence_symbol_encoding[symbol] = encoded_symbol
            self.__index_sequence_symbol_encoding[i] = symbol

        self.__train_dataset = train_dataset
        self.__end_of_sequence_symbol = end_of_sequence_symbol
        self.__random_seed = random_seed
        self.__round_limit = round_limit
        self.__activation_candidates = activation_candidates
        self.__optimizer_candidates = optimizer_candidates
        self.__batch_size_candidates = batch_size_candidates
        self.__dropout_candidates = dropout_candidates
        self.__layers_candidates = layers_candidates
        self.__train_X = None
        self.__train_Y = None
        self.__model = None
        self.__transformed_attribute_names: Union[None, List[str]] = None

    def mine_rules(self, dataset: TargetSequenceDataset = None) -> BlackboxRule:
        if dataset is not None and dataset != self.__train_dataset:
            raise ValueError()

        self.__train_X, self.__train_Y = self.__dataset_to_numpy_arrays(self.__train_dataset)

        params_definition = {
            'activation': self.__activation_candidates,
            'optimizer': self.__optimizer_candidates,
            'batch_size': self.__batch_size_candidates,
            'dropout': self.__dropout_candidates,
            'layers': self.__layers_candidates
        }
        permutations = set()
        self.__model = None
        best_accuracy = -1
        X_train, X_val, y_train, y_val = train_test_split(
            self.__train_X, self.__train_Y, random_state=self.__random_seed)
        random = Random(self.__random_seed)
        for _ in range(min(self.__round_limit, self.__compute_max_nr_of_permutations(params_definition))):
            params = self.__select_permutation(params_definition, random)
            while params in permutations:
                params = self.__select_permutation(params_definition, random)
            train_function = self._create_training_function()
            train_history, model = train_function(X_train, y_train, X_val, y_val, params)
            model_accuracy = max(train_history.history['val_accuracy'])
            if model_accuracy > best_accuracy:
                self.__model = model
                best_accuracy = model_accuracy
        return self

    @abstractmethod
    def _create_training_function(self):
        pass

    def execute(self, instance: TargetSequenceInstance) -> List[str]:
        dummy_dataset = TargetSequenceDataset(
            self.__train_dataset.get_categorical_attribute_names(),
            self.__train_dataset.get_numerical_attribute_names())
        dummy_dataset.add_instance(instance)

        X = self.__dataset_to_numpy_arrays(dummy_dataset, need_y=False)

        predicted_sequence = []
        for j in np.argmax(self.__model(X, training=False)[0,:,:], axis=1):
            decoded_symbol = self.__index_sequence_symbol_encoding[j]
            if decoded_symbol == self.__end_of_sequence_symbol:
                break
            predicted_sequence.append(decoded_symbol)
        return predicted_sequence

    def __compute_max_nr_of_permutations(self, params_definition: dict[str, list]) -> int:
        nr_of_permutations = 1
        for candidate_list in params_definition.values():
            nr_of_permutations *= len(candidate_list)
        return nr_of_permutations

    def __select_permutation(self, params_definition: dict[str, list], random: Random) -> dict[str,object]:
        return frozendict({
            name: random.choice(values)
            for name, values in params_definition.items()
        })

    def execute_with_explanation(
        self, instance: TargetSequenceDataset
    ) -> Tuple[List[str], List[lime.explanation.Explanation]]:
        """
        generates a sequence for the given instance and gives an explanation
        for each event of the sequence

        Parameters
        ----------
        instance : TargetSequenceDataset
            contains the features from which we want to generate the sequence

        Returns
        -------
        Tuple[List[str], List]
            first element of the tuple is the generated sequence
            second element of the tuple is a list of explanation where each
            element corresponds to an event in the generated sequence.
        """
        dummy_dataset = TargetSequenceDataset(
            self.__train_dataset.get_categorical_attribute_names(),
            self.__train_dataset.get_numerical_attribute_names())
        dummy_dataset.add_instance(instance)

        X = self.__dataset_to_numpy_arrays(dummy_dataset, need_y=False)

        predicted_sequence = self.execute(instance)
        explanation_list = []

        explainer = lime.lime_tabular.LimeTabularExplainer(
            self.__train_X,
            feature_names = self.__transformed_attribute_names,
            class_names = [
                symbol for i,symbol
                in sorted(self.__index_sequence_symbol_encoding.items())])

        for i in range(len(predicted_sequence)):
            predict_proba = lambda x: np.array(self.__model(x, training=False)[:,i,:])
            explanation_list.append(explainer.explain_instance(X[0,:], predict_proba, top_labels=1))

        return predicted_sequence, explanation_list

    def __dataset_to_numpy_arrays(self, dataset: TargetSequenceDataset, need_y: bool = True):
        dataset = self.__one_hot_encoder.transform(dataset)
        for attribute_name in dataset.get_numerical_attribute_names():
            for instance in dataset:
                instance[attribute_name] = (
                    instance[attribute_name] -
                    self.__mean_per_attribute[attribute_name]) / (
                        self.__stddev_per_attribute[attribute_name]
                )

        label_transformed_dataset = TargetSequenceDataset(
            dataset.get_categorical_attribute_names(),
            dataset.get_numerical_attribute_names())

        for instance in dataset:
            target_sequence = (
                instance.get_target_sequence() +
                (self.__end_of_sequence_symbol,) * self.__max_sequence_length)
            target_sequence = target_sequence[:self.__max_sequence_length]
            label_transformed_instance = TargetSequenceInstance(
                instance.get_id(), instance.get_features_dict(),
                target_sequence)
            label_transformed_dataset.add_instance(label_transformed_instance)

        X = np.array([
            [instance[attribute.get_name()]
             for attribute in dataset.get_attributes()]
            for instance in dataset
        ])

        self.__transformed_attribute_names = [
            attribute.get_name() for attribute in dataset.get_attributes()
        ]

        if not need_y:
            return X

        Y = np.ones((
            len(label_transformed_dataset), self.__max_sequence_length,
            len(self.__train_dataset.get_set_of_sequence_symbols()) + 1))
        Y[:] = np.nan

        for i, instance in enumerate(label_transformed_dataset):
            #We ignore unknown symbols in the encoding
            Y[i,:,:] = np.array([self.__sequence_symbol_encoding[symbol]
             for symbol in instance.get_target_sequence()
             if symbol in self.__sequence_symbol_encoding])

        return X,Y


