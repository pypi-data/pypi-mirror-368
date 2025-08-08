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

from sklearn.preprocessing import LabelEncoder

from mixed_naive_bayes import MixedNB

from prolothar_common.models.dataset import ClassificationDataset
from prolothar_common.models.dataset.transformer.label_encoding import LabelEncoding

from prolothar_rule_mining.rule_miner.classification.rules.sklearn import TrainedSklearnClassifier

class MixedNaiveBayesClassifier():
    """
    Interface to a naive bayes classifier for mixed data
    https://pypi.org/project/mixed-naive-bayes/
    """

    def __init__(self, alpha: float = 0.5):
        """
        configures the learning parameters for this MixedNaiveBayesClassifier

        Parameters
        ----------
        alpha : float, optional
            laplace smoothing parameter, by default 0.5
        """
        self.__alpha = alpha

    def mine_rules(self, dataset: ClassificationDataset) -> TrainedSklearnClassifier:
        """
        trains and returns a trained classifier on the given dataset.
        """
        categorical_encoder = LabelEncoding({
            attribute.get_name(): attribute.get_unique_values()
            for attribute in dataset.get_attributes()
            if attribute.is_categorical()
        })

        X = categorical_encoder.transform(dataset).to_dataframe().values

        label_encoder = LabelEncoder()
        y = [instance.get_class() for instance in dataset]
        y = label_encoder.fit_transform(y)

        naive_bayes = MixedNB(
            categorical_features=list(range(len(dataset.get_categorical_attribute_names()))),
            alpha=self.__alpha)
        naive_bayes.fit(X, y)

        return TrainedSklearnClassifier(
            dataset.get_numerical_attribute_names(),
            dataset.get_categorical_attribute_names(),
            naive_bayes,
            label_encoder,
            dataset_transformers = [categorical_encoder],
            preprocessors = []
        )

    def __repr__(self) -> str:
        return 'MixedNaiveBayesClassifier()'
