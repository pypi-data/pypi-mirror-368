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
from typing import List, Set, Generator, Dict, Tuple
from abc import ABC, abstractmethod

from graphviz import Digraph

from prolothar_common.levenshtein import EditOperationType

from prolothar_common.models.dataset.instance import Instance
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node

Backtrace = List[Tuple['ListOfRules', 'RuleLiteral', int]]
BacktraceResult = Tuple[List[str], Backtrace]

class Rule(ABC):
    """interface of a rule"""

    def execute(self, instance: Instance) -> List[str]:
        """generates a sequence for the given instance as input"""
        sequence = []
        self._execute(instance, sequence)
        return sequence

    @abstractmethod
    def _execute(self, instance: Instance, sequence: List[str]):
        """appends to a sequence for the given instance as input"""

    @abstractmethod
    def _execute_with_backtrace(
            self, parent: 'ListOfRules', index: int, instance: Instance,
            sequence: List[str], backtrace: Backtrace):
        """
        appends to the sequence and backtrace for the given instance as input
        """

    @abstractmethod
    def compute_mdl(self, set_of_symbols: Set[str],
                    nr_of_attributes: int) -> float:
        """computes the minimum-description-length of this rule
        Args:
            set_of_symbols:
                the of symbols that can occur in the target sequences
         """

    @abstractmethod
    def yield_subrules(self) -> Generator['Rule', None, None]:
        """yields all subrules recursively. This is useful to get all
        possible extension points of this rule
        """

    @abstractmethod
    def to_string(self, prefix='') -> str:
        """returns a human readable string representation of this rule
        Args:
            prefix:
                can be used for indentation
        """

    @abstractmethod
    def to_html(self) -> str:
        """returns a human readable html string representation of this rule"""

    def to_graphviz(self) -> Digraph:
        """
        returns a graphviz representation of the rules
        """
        graph = Digraph()
        self._add_to_digraph(graph)
        return graph

    @abstractmethod
    def _add_to_digraph(self, graph: Digraph) -> List[str]:
        """
        adds this rule to the given graphviz Digraph. returns the list of ids
        of end nodes for this rule for connections to following rules.
        """

    def to_eventflow_graph(self) -> EventFlowGraph:
        """
        creates an EventFlowGraph from this rule
        """
        graph = EventFlowGraph()
        self._add_to_eventflow_graph([graph.source], [graph.sink], graph)
        return graph

    @abstractmethod
    def _add_to_eventflow_graph(
        self, preceding_nodes: List[Node], next_nodes: List[Node],
        graph: EventFlowGraph) -> Tuple[List[Node], List[Node]]:
        """
        adds the rule to the EventFlowGraph. returns the source and the sink
        nodes of the added rule block
        """

    @abstractmethod
    def count_nr_of_terms(self) -> int:
        """
        returns the number of terms (atomic conditions).
        "If a > 2 and b <= 3 then append(x)" returns 2
        """

    @abstractmethod
    def get_appendable_symbols(self) -> Set[str]:
        """
        returns the set of symbols that can be appended by this rule
        """

    @abstractmethod
    def estimate_counter_change(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        """
        optimistically estimates how the edits_counter will change for the
        given instance if this rule is added to the model
        """

    @abstractmethod
    def compute_fast_data_mdl_gain_estimate_for_insert(
            self, instances: List[Instance], alphabet_size: int) -> float:
        """
        optimistically estimates how the data encoding will change after inserting
        this rule
        """

    @abstractmethod
    def compute_fast_data_mdl_gain_estimate_for_delete(
            self, instances: List[Instance]) -> float:
        """
        optimistically estimates how the data encoding will change after deleting
        this rule
        """

    @abstractmethod
    def estimate_counter_change_on_remove(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        """
        optimistically estimates how the edits_counter will change for the
        given instance if this rule is added to the model
        """

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return self.to_string()

    def __hash__(self) -> int:
        return hash(self.to_string())
