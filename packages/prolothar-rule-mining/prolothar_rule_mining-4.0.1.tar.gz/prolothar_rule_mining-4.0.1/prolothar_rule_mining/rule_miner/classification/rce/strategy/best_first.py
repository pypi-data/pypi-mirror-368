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
import sys

from prolothar_common.models.dataset import ClassificationDataset

from prolothar_rule_mining.rule_miner.classification.rce.strategy.abstract import CandidateSearchStrategy
from prolothar_rule_mining.rule_miner.classification.rce.candidate import CandidateCondition

from prolothar_rule_mining.models.conditions import AndCondition
from prolothar_rule_mining.models.conditions import OrCondition

class BestFirstCandidateSearch(CandidateSearchStrategy):
    """
    greedy search for conditions where only the most promising candidate
    per iteration is kept
    """

    def __init__(
            self, beta: float = 2.0, n_bins: int = 10,
            max_nr_of_candidates_for_extension: int = sys.maxsize):
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
        max_nr_of_candidates_for_extension : int, optional
            truncates the search space by reducing the number of candidates
            for extension of the current highest ranked condition.
            by default sys.maxsize
        """
        super().__init__(beta=beta, n_bins=n_bins)
        self.__max_nr_of_candidates_for_extension = max_nr_of_candidates_for_extension

    def _search_condition(self, base_candidates: List[CandidateCondition],
                          dataset: ClassificationDataset) -> CandidateCondition:
        best_candidate = base_candidates[0]
        remaining_candidates = [
            candidate for candidate in base_candidates[1:]
            if candidate.class_label == best_candidate.class_label
        ][:self.__max_nr_of_candidates_for_extension]

        return self.__extend_condition(best_candidate, remaining_candidates, dataset)

    def __extend_condition(
            self, candidate: CandidateCondition,
            remaining_candidates: List[CandidateCondition],
            dataset: ClassificationDataset) -> CandidateCondition:
        self._logger('extend candidate %r' % candidate)
        for i,other_candidate in enumerate(remaining_candidates):
            for new_condition in [
                    AndCondition([candidate.condition, other_candidate.condition]),
                    OrCondition([candidate.condition, other_candidate.condition])]:
                causal_effect = self._estimate_causal_effect(
                    new_condition, candidate.class_label, dataset)
                if causal_effect > candidate.causal_effect:
                    return self.__extend_condition(
                        CandidateCondition(new_condition,
                                           candidate.class_label,
                                           causal_effect),
                        remaining_candidates[i+1:],
                        dataset
                    )

        return candidate

    def __repr__(self) -> str:
        return 'BestFirstCandidateSearch(%d)' % self.__max_nr_of_candidates_for_extension