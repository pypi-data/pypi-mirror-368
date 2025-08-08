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
from typing import List, Set, Generator, Iterator, Dict, Callable, Tuple

from graphviz import Digraph

from prolothar_common.levenshtein import EditOperationType
import prolothar_common.mdl_utils as mdl_utils
from prolothar_common.models.dataset import Dataset
from prolothar_common.models.dataset.instance import Instance

from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule import Rule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule import Backtrace, BacktraceResult
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node

class ListOfRules(Rule):
    """an ordered list of rules"""
    def __init__(self, rules: List[Rule] = None):
        self.__subdataset = None
        self.__subdataset_supplier = None
        if rules is None:
            self.__rules: List[Rule] = []
        else:
            self.__rules: List[Rule] = rules

    def __eq__(self, other) -> bool:
        try:
            if len(self) != len(other):
                return False
            for a,b in zip(self.__rules, other.__rules):
                if a != b:
                    return False
            return True
        except AttributeError:
            return False

    def __hash__(self) -> int:
        value = 0
        for rule in self.__rules:
            value = value ^ hash(rule)
        return value

    def _execute(self, instance: Instance, sequence: List[str]):
        for rule in self.__rules:
            rule._execute(instance, sequence)

    def execute_with_backtrace(self, instance) -> BacktraceResult:
        """
        generates a sequence for the given instance as input and gives
        information about the rule literals that generated instance
        """
        sequence = []
        backtrace = []
        self._execute_with_backtrace(None, 0, instance, sequence, backtrace)
        return sequence, backtrace

    def _execute_with_backtrace(
            self, parent: 'ListOfRules', index: int, instance: Instance,
            sequence: List[str], backtrace: Backtrace):
        """
        appends to the sequence and backtrace for the given instance as input
        """
        for i,rule in enumerate(self.__rules):
            rule._execute_with_backtrace(self, i, instance, sequence, backtrace)

    def append_rule(self, rule: Rule):
        """appends the given rule to the end of this list"""
        self.__rules.append(rule)

    def compute_mdl(self, set_of_symbols: Set[str],
                    nr_of_attributes: int) -> float:
        #encode nr of rules in this list. can be 0 => + 1
        mdl = mdl_utils.L_N(len(self.__rules) + 1)
        for rule in self.__rules:
            #choice between append and if-else rule
            mdl += 1
            mdl += rule.compute_mdl(set_of_symbols, nr_of_attributes)
        return mdl

    def estimate_counter_change(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        """
        optimistically estimates how the edits_counter will change for the
        given instance if this rule is added to the model
        """
        for subrule in self.__rules:
            subrule.estimate_counter_change(
                edits_counter, missing_symbols_counter, instance)

    def estimate_counter_change_on_remove(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        """
        optimistically estimates how the edits_counter will change for the
        given instance if this rule is added to the model
        """
        for subrule in self.__rules:
            subrule.estimate_counter_change_on_remove(
                edits_counter, missing_symbols_counter, instance)

    def compute_fast_data_mdl_gain_estimate_for_insert(
            self, instances: List[Instance], alphabet_size: int) -> float:
        estimated_gain = 0
        for subrule in self.__rules:
            estimated_gain += subrule.compute_fast_data_mdl_gain_estimate_for_insert(
                instances, alphabet_size)
        return estimated_gain

    def compute_fast_data_mdl_gain_estimate_for_delete(
            self, instances: List[Instance]) -> float:
        estimated_gain = 0
        for subrule in self.__rules:
            estimated_gain += subrule.compute_fast_data_mdl_gain_estimate_for_delete(instances)
        return estimated_gain

    def yield_subrules(self) -> Generator['Rule', None, None]:
        for rule in self.__rules:
            yield rule
            yield from rule.yield_subrules()

    def get_appendable_symbols(self) -> Set[str]:
        appendable_symbols = set()
        for subrule in self.__rules:
            appendable_symbols.update(subrule.get_appendable_symbols())
        return appendable_symbols

    def __len__(self) -> int:
        """returns the number of rules in this list"""
        return len(self.__rules)

    def insert(self, i: int, rule: Rule):
        """insert a rule at the given index"""
        self.__rules.insert(i, rule)

    def remove_index(self, i: int) -> Rule:
        """removes the element at the given index and returns it"""
        return self.__rules.pop(i)

    def __getitem__(self, i: int):
        return self.__rules[i]

    def __setitem__(self, i: int, rule: Rule):
        self.__rules[i] = rule

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.__rules)

    def to_string(self, prefix='') -> str:
        return '\n'.join(rule.to_string(prefix=prefix) for rule in self.__rules)

    def to_html(self) -> str:
        return '<div id="%d" class="Rule ListOfRules">%s</div>' % (
            id(self), ''.join(rule.to_html() for rule in self.__rules))

    def _add_to_digraph(self, graph: Digraph) -> List[str]:
        if self.__rules:
            preceding_end_nodes = self.__rules[0]._add_to_digraph(graph)
        for rule in self.__rules[1:]:
            next_end_nodes = rule._add_to_digraph(graph)
            for preceding_end_node_id in preceding_end_nodes:
                graph.edge(preceding_end_node_id, str(id(rule)))
            preceding_end_nodes = next_end_nodes
        return preceding_end_nodes

    def _add_to_eventflow_graph(
        self, preceding_nodes: List[Node], next_nodes: List[Node],
        graph: EventFlowGraph) -> Tuple[List[Node], List[Node]]:
        """
        adds the rule to the EventFlowGraph
        """
        if len(self.__rules) == 0:
            return [], []
        elif len(self.__rules) == 1:
            return self.__rules[0]._add_to_eventflow_graph(preceding_nodes, next_nodes, graph)
        else:
            source_nodes, preceding_nodes = self.__rules[0]._add_to_eventflow_graph(preceding_nodes, [], graph)
            for rule in self.__rules[1:-1]:
                _, preceding_nodes = rule._add_to_eventflow_graph(preceding_nodes, [], graph)
            last_source_nodes, sink_nodes = self.__rules[-1]._add_to_eventflow_graph(
                preceding_nodes, next_nodes, graph)
            return source_nodes, sink_nodes

    def count_nr_of_terms(self) -> int:
        nr_of_terms = 0
        for subrule in self.__rules:
            nr_of_terms += subrule.count_nr_of_terms()
        return nr_of_terms

    def set_subdataset(self, subdataset: Dataset):
        """non-mandatory option to store a set of instances for this list
        of rules. can be used to track matching instances of rules
        """
        self.__subdataset = subdataset

    def set_subdataset_supplier(self, supplier: Callable[[], Dataset]):
        """non-mandatory option to store a set of instances for this list
        of rules. can be used to track matching instances of rules
        """
        self.__subdataset_supplier = supplier

    def get_list(self) -> List[Rule]:
        return self.__rules

    def get_subdataset(self) -> Dataset:
        """make sure to have set the subdataset via set_subdataset"""
        if self.__subdataset_supplier is not None:
            self.__subdataset = self.__subdataset_supplier()
            self.__subdataset_supplier = None
        return self.__subdataset