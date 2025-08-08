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
from typing import Any, Dict

from random import Random

from prolothar_common.models.dataset import Dataset
from prolothar_common.models.dataset.instance import Instance

from prolothar_rule_mining.models.conditions import Condition
from prolothar_rule_mining.models.conditions import EqualsCondition
from prolothar_rule_mining.models.conditions import LessThanCondition
from prolothar_rule_mining.models.conditions import GreaterThanCondition
from prolothar_rule_mining.models.conditions import AndCondition
from prolothar_rule_mining.models.conditions import OrCondition

class DatasetGenerator:
    """
    generates an artificial dataset with numerical and categorical attributes
    that are uniformly distributed
    """

    def __init__(self, nr_of_categorical_features: int = 0,
                 nr_of_categories: int = 3,
                 nr_of_numerical_features: int = 0,
                 nr_of_instances: int = 100,
                 max_condition_depth: int = 0,
                 random: Random = None):
        """create and configure a new dataset generator
        """
        self.__nr_of_categorical_features = nr_of_categorical_features
        if nr_of_categories < 2:
            raise ValueError('nr_of_categories must not be < 2, but was %d' %
                             nr_of_categories)
        self.__nr_of_categories = nr_of_categories
        self.__nr_of_numerical_features = nr_of_numerical_features
        if nr_of_instances < 1:
            raise ValueError('nr_of_instances must not be < 1, but was %d' %
                             nr_of_instances)
        self.__nr_of_instances = nr_of_instances
        if max_condition_depth < 0:
            raise ValueError('max_condition_depth must not be < 0, but was %d' %
                             max_condition_depth)
        self.__max_condition_depth = max_condition_depth
        self._random = random if random is not None else Random()

    def generate_features_only_dataset(self) -> Dataset:
        """generates a dataset without target sequences"""
        dataset = Dataset(
            ['cat_feature_%d' % i for i
             in range(self.__nr_of_categorical_features)],
            ['num_feature_%d' % i for i
             in range(self.__nr_of_numerical_features)])
        for i in range(self.__nr_of_instances):
            dataset.add_instance(Instance(i, self.__generate_features()))
        return dataset

    def __generate_features(self) -> Dict[str, Any]:
        features = {}
        for i in range(self.__nr_of_categorical_features):
            features['cat_feature_%d' % i] = str(self._random.choice(
                    range(self.__nr_of_categories)))
        for i in range(self.__nr_of_numerical_features):
            features['num_feature_%d' % i] = self._random.uniform(0,1)
        return features

    def _generate_condition(
            self, dataset: Dataset, depth: int = 0) -> Condition:
        attribute = self._random.choice(list(dataset.get_attributes()))
        if attribute.is_categorical():
            condition = EqualsCondition(attribute, self._random.choice(
                    list(attribute.get_unique_values())))
        elif attribute.is_numerical():
            condition = self._random.choice([LessThanCondition,
                                              GreaterThanCondition])
            #make sure not so select border value if possible
            sorted_values = list(sorted(attribute.get_unique_values()))
            if len(sorted_values) > 2:
                condition = condition(attribute, self._random.choice(
                        sorted_values[1:-1]))
            else:
                condition = condition(attribute, self._random.choice(
                        sorted_values))
        else:
            raise NotImplementedError
        if depth >= self.__max_condition_depth:
            return condition
        else:
            choice = self._random.randint(0,2)
            if choice == 0:
                return condition
            elif choice == 1:
                return AndCondition(
                        [condition, self._generate_condition(
                                dataset, depth=depth+1)])
            else:
                return OrCondition(
                        [condition, self._generate_condition(
                                dataset, depth=depth+1)])
