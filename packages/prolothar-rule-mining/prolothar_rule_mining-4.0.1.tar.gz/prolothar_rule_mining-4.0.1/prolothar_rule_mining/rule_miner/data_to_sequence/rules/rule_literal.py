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
from typing import List, Tuple, Generator

from graphviz import Digraph

from prolothar_common.models.dataset.instance import Instance

from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule import Rule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule import Backtrace

class RuleLiteral(Rule):
    """
    base class for rules without subrules
    """
    def yield_subrules(self) -> Generator['Rule', None, None]:
        #there are no subrules
        return
        yield

    def count_nr_of_terms(self) -> int:
        return 0

    def appears_in_sequence(self, sequence: Tuple[str]) -> bool:
        """returns True iff this rule literal appears in the given sequence"""
        pass

    def _execute_with_backtrace(
            self, parent: 'ListOfRules', index: int, instance: Instance,
            sequence: Tuple[str], backtrace: Backtrace):
        self._execute(instance, sequence)
        backtrace.append((parent, self, index))

    def _add_to_digraph(self, graph: Digraph) -> List[str]:
        graph.node(str(id(self)), label=str(self))
        return [str(id(self))]
