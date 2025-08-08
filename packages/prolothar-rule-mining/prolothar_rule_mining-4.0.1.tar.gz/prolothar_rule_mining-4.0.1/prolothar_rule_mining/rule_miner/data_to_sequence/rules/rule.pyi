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
from abc import ABC

from graphviz import Digraph

from prolothar_common.models.dataset.instance import Instance
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph

class Rule(ABC):
    """interface of a rule"""

    def execute(self, instance: Instance) -> List[str]:
        """generates a sequence for the given instance as input"""
        ...

    def to_string(self, prefix='') -> str:
        """returns a human readable string representation of this rule
        Args:
            prefix:
                can be used for indentation
        """
        ...

    def to_html(self) -> str:
        """returns a human readable html string representation of this rule"""
        ...

    def to_graphviz(self) -> Digraph:
        """
        returns a graphviz representation of the rules
        """
        ...

    def to_eventflow_graph(self) -> EventFlowGraph:
        """
        creates an EventFlowGraph from this rule
        """
        ...

    def count_nr_of_terms(self) -> int:
        """
        returns the number of terms (atomic conditions).
        "If a > 2 and b <= 3 then append(x)" returns 2
        """
        ...
