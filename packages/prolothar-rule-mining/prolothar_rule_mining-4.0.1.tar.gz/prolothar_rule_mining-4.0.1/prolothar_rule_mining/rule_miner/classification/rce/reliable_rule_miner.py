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
based on
    https://eda.mmci.uni-saarland.de/pubs/2021/dice-budhathoki,boley,vreeken.pdf
"""

from typing import Callable

from collections import defaultdict

from prolothar_common.models.dataset import ClassificationDataset
from prolothar_common.func_tools import do_nothing

from prolothar_rule_mining.rule_miner.classification.rules import ListOfRules
from prolothar_rule_mining.rule_miner.classification.rules import IfThenElseRule
from prolothar_rule_mining.rule_miner.classification.rules import ReturnClassRule
from prolothar_rule_mining.rule_miner.classification.rules import FirstFiringRuleModel

from prolothar_rule_mining.rule_miner.classification.rce.strategy.abstract import CandidateSearchStrategy
from prolothar_rule_mining.rule_miner.classification.rce.strategy.best_first import BestFirstCandidateSearch
from prolothar_rule_mining.models.conditions import OrCondition

class ReliableRuleMiner():
    """
    based on
    https://eda.mmci.uni-saarland.de/pubs/2021/dice-budhathoki,boley,vreeken.pdf
    """

    def __init__(self, search_strategy: CandidateSearchStrategy = BestFirstCandidateSearch(),
                 logger: Callable[[str], None] = print):
        self.__search_strategy = search_strategy
        if logger is None:
            logger = do_nothing
        self.__logger = logger
        search_strategy.set_logger(logger)

    def mine_rules(self, dataset: ClassificationDataset) -> FirstFiringRuleModel:
        rules = ListOfRules()

        while len(dataset) > 1:
            best_candidate = self.__search_strategy.create_next_condition(dataset)
            if best_candidate is None:
                break
            rules.append_rule(IfThenElseRule(
                best_candidate.condition.compress(),
                if_branch=ListOfRules([
                    ReturnClassRule(best_candidate.class_label)
                ])
            ))

            old_length = len(dataset)
            dataset = best_candidate.condition.divide_dataset(dataset)[1]
            if len(dataset) == old_length:
                break

        if len(dataset) > 0:
            majority_class = self.__get_majority_class(dataset)
            self.__logger('append majority class rule "%s"' % majority_class)
            rules.append_rule(ReturnClassRule(majority_class))

        return FirstFiringRuleModel(self.__postprocess_rules(rules))

    def __get_majority_class(self, dataset: ClassificationDataset) -> str:
        counter = defaultdict(int)
        for instance in dataset:
            counter[instance.get_class()] += 1
        return max(counter, key=counter.get)

    def __postprocess_rules(self, rules: ListOfRules) -> ListOfRules:
        # remove unnecessary conditions at the end of rule list
        # "If X then A; If Y then B; If Z then B; B" is reduced to
        # "If X then A; B"
        if isinstance(rules[-1], IfThenElseRule):
            last_if_then_else_rule = rules.remove_index(-1)
            rules.append_rule(last_if_then_else_rule.get_if_branch()[0])
            while len(rules) > 1 and isinstance(rules[-2], IfThenElseRule) \
            and rules[-1].get_class_label() == rules[-2].get_if_branch()[0].get_class_label():
                rules.remove_index(-2)

        if len(rules) <= 1:
            return rules

        #Merge rules with same effect that directly follow each other
        pruned_rules = ListOfRules()

        last_rule = rules[0]
        last_class_label = last_rule.get_if_branch()[0].get_class_label()
        pruned_rules.append_rule(last_rule)
        for current_rule in rules[1:-1]:
            current_class_label = current_rule.get_if_branch()[0].get_class_label()
            if current_class_label == last_class_label:
                last_rule.set_condition(OrCondition([
                    last_rule.get_condition(), current_rule.get_condition()
                ]).compress())
            else:
                last_rule.set_condition(last_rule.get_condition().compress())
                last_rule = current_rule
                last_class_label = current_class_label
                pruned_rules.append_rule(current_rule)
        if len(rules) > 1:
            pruned_rules.append_rule(rules[-1])

        return pruned_rules

    def __repr__(self) -> str:
        return 'ReliableRuleMiner(search_strategy=%r)' % self.__search_strategy
