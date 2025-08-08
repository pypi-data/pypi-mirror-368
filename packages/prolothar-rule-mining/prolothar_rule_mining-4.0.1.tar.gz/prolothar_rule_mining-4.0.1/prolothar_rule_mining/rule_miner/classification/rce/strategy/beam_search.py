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

from prolothar_common.models.dataset import ClassificationDataset

from prolothar_rule_mining.rule_miner.classification.rce.strategy.abstract import CandidateSearchStrategy
from prolothar_rule_mining.rule_miner.classification.rce.candidate import CandidateCondition
from prolothar_rule_mining.rule_miner.classification.rce.candidate import VectorCandidateCondition

from prolothar_rule_mining.models.conditions import AndCondition
from prolothar_rule_mining.models.conditions import OrCondition

class BeamSearch(CandidateSearchStrategy):
    """
    greedy search for conditions where only the top-k most promising candidate
    per iterations are kept
    """

    def __init__(
            self, beta: float = 2.0, n_bins: int = 10, beam_width: int = 5,
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
        beam_width : int, optional
            width parameter of the beam search. the higher, the more runtime
            is needed but there is less danger to miss better candidates in
            later iterations
        max_nr_of_base_candidates : int, optional
            the number of base candidates to keep for extension during search.
            default means no limitation. the limitation is useful, if some
            categorical attributes have many different values such as an ID.
        """
        super().__init__(beta=beta, n_bins=n_bins,
                         max_nr_of_base_candidates=max_nr_of_base_candidates)
        self.__beam_width = beam_width

    def _search_condition(self, base_candidates: List[CandidateCondition],
                          dataset: ClassificationDataset) -> CandidateCondition:
        current_candidates = base_candidates[:self.__beam_width]
        while True:
            self._logger('current candidates:')
            for candidate in current_candidates:
                self._logger(repr(candidate))
            extended_candidates = self.__extend_candidates(
                current_candidates, base_candidates, dataset)
            next_candidates = []
            for candidate in extended_candidates:
                if len(next_candidates) < self.__beam_width \
                and candidate.causal_effect > current_candidates[0].causal_effect:
                    next_candidates.append(candidate)
                else:
                    break
            if not next_candidates:
                self._logger('return candidate %r' % current_candidates[0])
                return current_candidates[0]
            current_candidates = next_candidates
            current_candidates.sort(reverse=True)

    def __extend_candidates(
            self, current_candidates: List[VectorCandidateCondition],
            base_candidates: List[VectorCandidateCondition],
            dataset: ClassificationDataset) -> List[CandidateCondition]:
        extended_candidates = []

        for candidate in current_candidates:
            for base_candidate in base_candidates:
                if candidate is not base_candidate \
                and candidate.class_label == base_candidate.class_label:
                    and_condition = AndCondition([
                        candidate.condition, base_candidate.condition
                    ])
                    condition_hold_vector = (
                        candidate.condition_hold_vector &
                        base_candidate.condition_hold_vector)
                    extended_candidates.append(
                        VectorCandidateCondition(
                            and_condition,
                            condition_hold_vector,
                            candidate.class_label,
                            candidate.class_label_hold_vector,
                            self._estimate_causal_effect_with_numpy(
                                condition_hold_vector,
                                candidate.class_label_hold_vector,
                                dataset,
                                candidate.class_label
                            )
                        )
                    )

                    or_condition = OrCondition([
                        candidate.condition, base_candidate.condition
                    ])
                    condition_hold_vector = (
                        candidate.condition_hold_vector |
                        base_candidate.condition_hold_vector)
                    extended_candidates.append(
                        VectorCandidateCondition(
                            or_condition,
                            condition_hold_vector,
                            candidate.class_label,
                            candidate.class_label_hold_vector,
                            self._estimate_causal_effect_with_numpy(
                                condition_hold_vector,
                                candidate.class_label_hold_vector,
                                dataset,
                                candidate.class_label
                            )
                        )
                    )

        return extended_candidates

    def __repr__(self) -> str:
        return 'BeamSearch(%d)' % self.__beam_width