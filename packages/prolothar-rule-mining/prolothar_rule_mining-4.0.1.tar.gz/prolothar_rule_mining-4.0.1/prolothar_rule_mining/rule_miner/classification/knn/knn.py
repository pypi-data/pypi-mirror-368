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
K nearest neighbor classifier
"""

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier

from prolothar_common.models.dataset import ClassificationDataset
from prolothar_common.models.dataset.transformer.one_hot_encoding import OneHotEncoding

from prolothar_rule_mining.rule_miner.classification.rules.sklearn import TrainedSklearnClassifier

class KnnClassifier():
    """
    Interface to the K nearest neighbor classifier of sklearn
    """

    def __init__(self, k: int = 5, nr_of_jobs: int = -1, knn_algorithm: str = 'auto'):
        self.__k = k
        self.__nr_of_jobs = nr_of_jobs
        self.__knn_algorithm = knn_algorithm

    def mine_rules(self, dataset: ClassificationDataset) -> TrainedSklearnClassifier:
        """
        trains and returns a KNN classifier on the given dataset.
        """
        one_hot_encoder = OneHotEncoding({
            attribute.get_name(): attribute.get_unique_values()
            for attribute in dataset.get_attributes()
            if attribute.is_categorical()
        })

        X = one_hot_encoder.transform(dataset).to_dataframe().values
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)

        label_encoder = LabelEncoder()
        y = [instance.get_class() for instance in dataset]
        y = label_encoder.fit_transform(y)

        knn = KNeighborsClassifier(
            n_neighbors=self.__k, n_jobs=self.__nr_of_jobs,
            algorithm=self.__knn_algorithm
        )
        knn.fit(X, y)

        return TrainedSklearnClassifier(
            dataset.get_numerical_attribute_names(),
            dataset.get_categorical_attribute_names(),
            knn,
            label_encoder,
            dataset_transformers = [one_hot_encoder],
            preprocessors = [scaler]
        )

    def __repr__(self) -> str:
        return 'KnnClassifier(k=%d, nr_of_jobs=%d)' % (self.__k, self.__nr_of_jobs)
