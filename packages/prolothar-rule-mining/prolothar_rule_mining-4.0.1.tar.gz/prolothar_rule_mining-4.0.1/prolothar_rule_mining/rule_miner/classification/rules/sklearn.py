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
from typing import List, Set, Dict

import itertools

from sklearn.preprocessing import LabelEncoder
from sklearn.base import TransformerMixin, ClassifierMixin

from prolothar_common.models.dataset import Dataset
from prolothar_common.models.dataset.instance import Instance
from prolothar_common.models.dataset.transformer.dataset_transformer import DatasetTransformer

from prolothar_rule_mining.rule_miner.classification.rules.rule import Rule


class TrainedSklearnClassifier(Rule):
    """
    creates a rule interface to a fitted sklearn classifer
    """

    def __init__(
        self, numerical_attribute_names: List[str],
        categorical_attribute_names: List[str],
        classifier: ClassifierMixin,
        label_encoder: LabelEncoder,
        dataset_transformers: List[DatasetTransformer],
        preprocessors: List[TransformerMixin]):
        """
        creates a rule interface to a sklearn classifer

        Parameters
        ----------
        numerical_attribute_names : List[str]
            names of the numerical attributes in the dataset. this is used
            to create a dummy dataset for instances at prediction time for
            the necessary data transformation.
        categorical_attribute_names : List[str]
            names of the numerical attributes in the dataset. this is used
            to create a dummy dataset for instances at prediction time for
            the necessary data transformation.
        classifier : ClassifierMixin
            the fitted sklearn classifier
        label_encoder : LabelEncoder
            needed to map the sklearn output to the class in the dataset
        dataset_transformers : List[DatasetTransformer]
            preprocessors (e.g. OneHotEncoding) on the Dataset model
        preprocessors : List[TransformerMixin]
            preprocessors (e.g. MinMaxScaling) after the dummy Dataset of the
            instance to predict has been converted to a numpy vector
        """
        self.__numerical_attribute_names = numerical_attribute_names
        self.__categorical_attribute_names = categorical_attribute_names
        self.__classifier = classifier
        self.__label_encoder = label_encoder
        self.__dataset_transformers = dataset_transformers
        self.__preprocessors = preprocessors

    def predict(self, instance: Instance) -> str:
        """predicts a class for the given instance as input"""
        X = self.__transform_instance(instance)
        return self.__label_encoder.inverse_transform(self.__classifier.predict(X))[0]

    def __transform_instance(self, instance: Instance):
        instance = Instance(instance.get_id(), {
            attribute_name: instance[attribute_name]
            for attribute_name in itertools.chain(
                self.__categorical_attribute_names,
                self.__numerical_attribute_names
            )
        })
        dummy_dataset = Dataset(
            self.__categorical_attribute_names, self.__numerical_attribute_names)
        dummy_dataset.add_instance(instance)
        for transformer in self.__dataset_transformers:
            transformer.transform(dummy_dataset, inplace=True)
        X = dummy_dataset.to_dataframe().values
        for preprocessor in self.__preprocessors:
            X = preprocessor.transform(X)
        return X

    def predict_proba(self, instance: Instance) -> Dict[str, float]:
        """
        predicts a probability per class for the given instance as input.
        throws an Error if the underlying sklearn classifier does not support
        probabilistic predictions
        """
        X = self.__transform_instance(instance)
        return {
            self.__label_encoder.inverse_transform([i])[0]: probability
            for i, probability in enumerate(self.__classifier.predict_proba(X)[0])
        }

    def to_string(self, prefix='') -> str:
        """returns a human readable string representation of this rule
        Args:
            prefix:
                can be used for indentation
        """
        return str(self.__classifier)

    def to_html(self) -> str:
        """returns a human readable html string representation of this rule"""
        return self.to_string()

    def get_set_of_output_classes(self) -> Set[str]:
        """
        returns the set of classes this rule can return during predict()
        """
        return self.__label_encoder.classes_
