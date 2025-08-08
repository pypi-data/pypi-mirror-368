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
from typing import Tuple

from random import Random

from prolothar_common.models.dataset import ClassificationDataset, Dataset
from prolothar_common.models.dataset.instance import ClassificationInstance

from prolothar_rule_mining.models.dataset_generator.dataset_generator import DatasetGenerator
from prolothar_rule_mining.rule_miner.classification.rules import Rule
from prolothar_rule_mining.rule_miner.classification.rules import FirstFiringRuleModel
from prolothar_rule_mining.rule_miner.classification.rules import ListOfRules
from prolothar_rule_mining.rule_miner.classification.rules import ReturnClassRule
from prolothar_rule_mining.rule_miner.classification.rules import IfThenElseRule

class ClassificationDatasetGenerator(DatasetGenerator):
    """
    generates an artificial dataset and rules for classification
    under some parameters
    """

    def __init__(self, nr_of_categorical_features: int = 0,
                 nr_of_categories: int = 3,
                 nr_of_numerical_features: int = 0,
                 nr_of_instances: int = 100,
                 max_condition_depth: int = 0,
                 nr_of_classes: int = 10,
                 random: Random = None):
        super().__init__(
            nr_of_categorical_features = nr_of_categorical_features,
            nr_of_categories = nr_of_categories,
            nr_of_numerical_features = nr_of_numerical_features,
            nr_of_instances = nr_of_instances,
            max_condition_depth = max_condition_depth,
            random = random)
        if nr_of_classes < 2:
            raise ValueError('nr_of_classes must not be < 2, but was %d' %
                             nr_of_classes)
        self.__nr_of_classes = nr_of_classes

    def generate(self) -> Tuple[ClassificationDataset, Rule]:
        """
        returns an artificially generated dataset and rules for the
        classification of instances
        """
        dataset = self.generate_features_only_dataset()
        rule = self.__generate_list_of_rules(dataset)
        dataset = self.apply_rule_to_dataset(dataset, rule)
        return dataset, rule

    def __generate_list_of_rules(self, dataset: Dataset) -> Rule:
        class_label_list = list(map(str, range(self.__nr_of_classes)))
        self._random.shuffle(class_label_list)
        rule = ListOfRules()
        if dataset.get_nr_of_attributes() > 0:
            for class_label in class_label_list[:-1]:
                condition = self._generate_condition(dataset)
                rule.append_rule(IfThenElseRule(
                    condition,
                    if_branch=ListOfRules([
                        ReturnClassRule(class_label)
                    ])
                ))
                dataset = condition.divide_dataset(dataset)[1]
                if not dataset:
                    return FirstFiringRuleModel(rule)
        rule.append_rule(ReturnClassRule(class_label_list[-1]))
        return FirstFiringRuleModel(rule)

    def apply_rule_to_dataset(
            self, dataset: Dataset, rule: Rule) -> ClassificationDataset:
        dataset_with_classes = ClassificationDataset(
                [attribute.get_name() for attribute in dataset.get_attributes()
                 if attribute.is_categorical()],
                [attribute.get_name() for attribute in dataset.get_attributes()
                 if attribute.is_numerical()])
        for instance in dataset:
            dataset_with_classes.add_instance(ClassificationInstance(
                    instance.get_id(), instance.get_features_dict(),
                    rule.predict(instance)))
        return dataset_with_classes