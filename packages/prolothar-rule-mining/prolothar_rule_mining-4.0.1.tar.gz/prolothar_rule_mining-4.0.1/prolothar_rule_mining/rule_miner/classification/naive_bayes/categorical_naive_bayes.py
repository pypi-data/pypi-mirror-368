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
naive bayes classifier
"""

import numpy as np
from sklearn.preprocessing import LabelEncoder

from sklearn.naive_bayes import CategoricalNB

from prolothar_common.models.dataset import ClassificationDataset
from prolothar_common.models.dataset.transformer.label_encoding import LabelEncoding
from prolothar_common.models.dataset.transformer import TrainableQuantileBasedDiscretization
from prolothar_common.models.dataset.transformer import RemoveAttributesWithOneUniqueValue

from prolothar_rule_mining.rule_miner.classification.rules.sklearn import TrainedSklearnClassifier

class CategoricalNaiveBayesClassifier():
    """
    Interface to a naive bayes classifier for categorical data
    https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.CategoricalNB.html
    Non-categorical data will be discretized
    """

    def __init__(self, nr_of_bins: int = 5):
        self.__nr_of_bins = nr_of_bins

    def mine_rules(self, dataset: ClassificationDataset) -> TrainedSklearnClassifier:
        """
        trains and returns a trained classifier on the given dataset.
        """
        transformed_dataset = dataset.copy()

        RemoveAttributesWithOneUniqueValue().transform(transformed_dataset, inplace=True)
        categorical_feature_names = dataset.get_categorical_attribute_names()
        numerical_feature_names = dataset.get_numerical_attribute_names()

        numerical_encoder = TrainableQuantileBasedDiscretization.train(
            transformed_dataset, self.__nr_of_bins)
        numerical_encoder.transform(transformed_dataset, inplace=True)

        categorical_encoder = LabelEncoding({
            attribute.get_name(): attribute.get_unique_values()
            for attribute in transformed_dataset.get_attributes()
            if attribute.is_categorical()
        })
        categorical_encoder.transform(transformed_dataset, inplace=True)

        X = transformed_dataset.to_dataframe().values

        label_encoder = LabelEncoder()
        y = [instance.get_class() for instance in transformed_dataset]
        y = label_encoder.fit_transform(y)

        if transformed_dataset.get_nr_of_attributes() == 0:
            X = np.ones((len(y), 1))
        naive_bayes = CategoricalNB()
        naive_bayes.fit(X, y)

        return TrainedSklearnClassifier(
            numerical_feature_names,
            categorical_feature_names,
            naive_bayes,
            label_encoder,
            dataset_transformers = [numerical_encoder, categorical_encoder],
            preprocessors = []
        )

    def __repr__(self) -> str:
        return 'CategoricalNaiveBayesClassifier()'
