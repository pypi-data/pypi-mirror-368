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
this package contains the rule models. the __init__.py imports all the rules
such that the paths in existing code do not need to be adapted. in a former
version of this code, all models were part of rules.py(x)
"""
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule import Rule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule import Backtrace
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule import BacktraceResult
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.blackbox  import BlackboxRule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.list_of_rules import ListOfRules
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.if_then_else import IfThenElseRule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule_literal import RuleLiteral
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.append_rule import AppendRule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.append_subsequence import AppendSubsequenceRule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.classification_rule import ClassificationRule
