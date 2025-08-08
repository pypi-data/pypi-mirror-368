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
from typing import List, Callable, Generator

from math import sqrt
import more_itertools
import pandas as pd
import numpy as np

from prolothar_common.models.dataset import ClassificationDataset
from prolothar_common.models.dataset.attributes import Attribute

from prolothar_rule_mining.rule_miner.classification.rce.candidate import CandidateCondition
from prolothar_rule_mining.rule_miner.classification.rce.candidate import VectorCandidateCondition
from prolothar_rule_mining.rule_miner.classification.rce.candidate import LazyVectorCandidateCondition
from prolothar_rule_mining.models.conditions import Condition
from prolothar_rule_mining.models.conditions import EqualsCondition
from prolothar_rule_mining.models.conditions import LessThanCondition
from prolothar_rule_mining.models.conditions import LessOrEqualCondition
from prolothar_rule_mining.models.conditions import GreaterThanCondition

cdef class CandidateSearchStrategy():
    """
    template for any strategy that searches for a classification rule given
    a dataset
    """
    cdef float __beta
    cdef int __n_bins
    cdef int __max_nr_of_base_candidates

    def __init__(self, beta: float = 2.0, n_bins: int = 10,
                 max_nr_of_base_candidates: int = -1):
        """
        configuration of the condition search

        Parameters
        ----------
        beta : float, optional
            correction factor for the estimation of the effect of a condition
            0 means the correction terms are removed, by default 2.0
            for a better understanding of this paramter look into
            https://eda.mmci.uni-saarland.de/pubs/2021/dice-budhathoki,boley,vreeken.pdf
        n_bins : int, optional
            number of bins for discretization of numerical features. this reduces
            the search space for "greater" and "less than" conditions with the
            cost of accuracy. a higher number leads to a higher accuracy with
            the cost of additional runtime. by default 10
        max_nr_of_base_candidates : int, optional
            the number of base candidates to keep for extension during search.
            default means no limitation. the limitation is useful, if some
            categorical attributes have many different values such as an ID.
        """
        self.__beta = beta
        self.__n_bins = n_bins
        self._logger = print
        self.__max_nr_of_base_candidates = max_nr_of_base_candidates

    def set_logger(self, logger: Callable[[str], None]):
        self._logger = logger

    def create_next_condition(self, dataset: ClassificationDataset) -> CandidateCondition:
        """
        searches for the next best condition used for classification

        Parameters
        ----------
        dataset : ClassificationDataset
            a dataset with attributes and labels.

        Returns
        -------
        CandidateCondition
            a condition on the attributes of the dataset that can be used
            to classify a label. if no condition is found for some reasons
            (e.g. the search strategy may decide that the condition has not
            enough evidence), None is returned.
        """
        class_label_vector_map: dict = self.__create_class_label_vector_map(dataset)

        conditions = []
        for attribute in dataset.get_attributes():
            conditions.extend(self.__yield_condition_candidates(attribute))

        candidates = []
        for condition in conditions:
            if isinstance(condition, EqualsCondition):
                candidate_generator = self.__generate_equals_candidates
            else:
                candidate_generator = self.__generate_numeric_candidates
            for candidate in candidate_generator(dataset, condition, class_label_vector_map):
                if candidate.causal_effect > 0:
                    candidates.append(candidate)

        candidates.sort(reverse=True)

        if not candidates:
            return None

        if self.__max_nr_of_base_candidates is not None \
        and self.__max_nr_of_base_candidates > 0:
            candidates = candidates[:self.__max_nr_of_base_candidates]
        return self._search_condition(candidates, dataset)

    def __generate_equals_candidates(
            self, dataset: ClassificationDataset, condition: EqualsCondition,
            class_label_vector_map) -> Generator[CandidateCondition, None, None]:
        for class_label in dataset.get_set_of_classes():
            effect = self.__compute_causal_effect_on_equals_condition(
                condition, class_label, dataset)
            yield LazyVectorCandidateCondition(
                condition, dataset, class_label, class_label_vector_map[class_label], effect)

    def __generate_numeric_candidates(
            self, dataset: ClassificationDataset, condition: EqualsCondition,
            class_label_vector_map) -> Generator[CandidateCondition, None, None]:
        condition_holds_vector = self.__compute_condition_holds_vector(
            dataset, condition)
        for class_label in dataset.get_set_of_classes():
            effect = self._estimate_causal_effect_with_numpy(
                condition_holds_vector, class_label_vector_map[class_label],
                dataset, class_label)
            yield VectorCandidateCondition(
                condition, condition_holds_vector, class_label,
                class_label_vector_map[class_label], effect)

    def _search_condition(self, base_candidates: List[VectorCandidateCondition],
                          dataset: ClassificationDataset) -> CandidateCondition:
        """
        uses the list of ranked candidates as a base for search of the best condition
        to distinguish class labels in the dataset

        Parameters
        ----------
        base_candidates : List[VectorCandidateCondition]
            ranked and non-empty list of candidate conditions. the first condition
            has the highest effect on its label
        dataset : ClassificationDataset
            a dataset with attributes and labels.

        Returns
        -------
        CandidateCondition
            the found candidate condition with highest effect on its class label
            derived from the list of base candidates
        """
        raise NotImplementedError()

    def __yield_condition_candidates(self, attribute: Attribute):
        if attribute.is_categorical():
            for value in attribute.get_unique_values():
                yield EqualsCondition(attribute, value)
        elif attribute.get_nr_of_unique_values() <= self.__n_bins:
            for a,b in more_itertools.pairwise(sorted(attribute.get_unique_values())):
                yield LessThanCondition(attribute, (a+b)/2)
                yield GreaterThanCondition(attribute, (a+b)/2)
        else:
            interval_list = sorted(set(pd.qcut([v for v in attribute.get_unique_values()],
                                   self.__n_bins, duplicates='drop')))
            for interval in interval_list[:-1]:
                yield GreaterThanCondition(attribute, interval.right)
                yield LessOrEqualCondition(attribute, interval.right)
                #compensate for bad discretization
                yield LessOrEqualCondition(attribute, interval.mid)

    def _estimate_causal_effect(
            self, condition: Condition, class_label: str,
            dataset: ClassificationDataset) -> float:
        """
        estimates the effect of the condition on the given class_label in the
        given dataset

        Parameters
        ----------
        condition : Condition
            [description]
        class_label : str
            [description]
        dataset : ClassificationDataset
            [description]

        Returns
        -------
        float
            will be a number between -1 and 1
            -1 is the highest possible negative effect on the class label,
                i.e. instances with this condition do not have the label
            1 is the highest possible positive effect on the class label,
                i.e. instances with this condition have the label
        """

        if isinstance(condition, EqualsCondition):
            return self.__compute_causal_effect_on_equals_condition(
                condition, class_label, dataset)
        else:
            return self.__compute_causal_effect_by_counting_when_condition_holds(
                condition, class_label, dataset)

    def __compute_causal_effect_by_counting_when_condition_holds(
            self, condition: Condition, class_label: str,
            dataset: ClassificationDataset) -> float:
        cdef int n_condition_is_true = 0
        cdef int n_condition_is_false = 0
        cdef int n_condition_is_true_and_target_is_true = 0
        cdef int n_condition_is_false_and_target_is_true = 0

        for instance in dataset:
            if condition.check_instance(instance):
                n_condition_is_true += 1
                if instance.get_class() == class_label:
                    n_condition_is_true_and_target_is_true += 1
            else:
                n_condition_is_false += 1
                if instance.get_class() == class_label:
                    n_condition_is_false_and_target_is_true += 1

        return self.__compute_causal_effect(
            n_condition_is_true, n_condition_is_false,
            n_condition_is_true_and_target_is_true,
            n_condition_is_false_and_target_is_true)

    def __compute_causal_effect_on_equals_condition(
            self, condition: Condition, class_label: str,
            dataset: ClassificationDataset) -> float:
        attribute_name = condition.get_attribute().get_name()
        n_condition_is_true = dataset.get_count_for_category(
            attribute_name, condition.get_value())
        n_condition_is_true_and_target_is_true = dataset.get_count_for_category_and_class(
            attribute_name, condition.get_value(), class_label)
        return self.__compute_causal_effect(
            n_condition_is_true,
            len(dataset) - n_condition_is_true,
            n_condition_is_true_and_target_is_true,
            dataset.get_class_count(class_label) - n_condition_is_true_and_target_is_true)

    def _estimate_causal_effect_with_numpy(
            self, condition_holds_vector, class_holds_vector,
            dataset: ClassificationDataset, class_label: str) -> float:
        cdef int n_condition_is_true = np.count_nonzero(condition_holds_vector)
        cdef int n_condition_is_true_and_target_is_true = np.count_nonzero(
            condition_holds_vector & class_holds_vector)
        return self.__compute_causal_effect(
            n_condition_is_true,
            len(dataset) - n_condition_is_true,
            n_condition_is_true_and_target_is_true,
            dataset.get_class_count(class_label) - n_condition_is_true_and_target_is_true)

    cdef float __compute_causal_effect(
            self, n_condition_is_true: int, n_condition_is_false: int,
            n_condition_is_true_and_target_is_true: int,
            n_condition_is_false_and_target_is_true: int):
        cdef float causal_effect
        causal_effect = (n_condition_is_true_and_target_is_true + 1) \
                      / (n_condition_is_true + 2)
        causal_effect -= (n_condition_is_false_and_target_is_true + 1) \
                       / (n_condition_is_false + 2)
        causal_effect -= 0.5 * self.__beta \
                       / sqrt(n_condition_is_true + 2)
        causal_effect -= 0.5 * self.__beta \
                       / sqrt(n_condition_is_false + 2)
        return causal_effect

    def __create_class_label_vector_map(self, dataset: ClassificationDataset) -> dict:
        label_vector_map = {}
        for label in dataset.get_set_of_classes():
            label_vector_map[label] = np.array(
                [instance.get_class() == label for instance in dataset], dtype=bool)
        return label_vector_map

    def __compute_condition_holds_vector(
            self, dataset: ClassificationDataset, condition: Condition):
        return np.array(
            [condition.check_instance(instance) for instance in dataset], dtype=bool)
