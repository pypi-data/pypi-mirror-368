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

from graphviz import Digraph

from prolothar_common.models.dataset import Dataset
from prolothar_common.models.dataset.instance import Instance

from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule import Rule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule import Backtrace
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule_literal import RuleLiteral
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.list_of_rules import ListOfRules
from prolothar_rule_mining.models.conditions import Condition
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node
from prolothar_common.levenshtein import EditOperationType

class IfThenElseRule(Rule):
    """rule with an if and an else branch"""
    def __init__(self, condition: Condition, if_branch: ListOfRules = None,
                 else_branch: ListOfRules = None):
        self.__condition = condition
        if if_branch is None:
            self.__if_branch = ListOfRules()
        else:
            self.__if_branch = if_branch
        if else_branch is None:
            self.__else_branch = ListOfRules()
        else:
            self.__else_branch = else_branch

    def __eq__(self, other) -> bool:
        try:
            return (self.__condition == other.__condition and
                    self.__if_branch == other.__if_branch and
                    self.__else_branch == other.__else_branch)
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return hash((self.__condition, self.__if_branch, self.__else_branch))

    def get_if_branch(self) -> ListOfRules:
        return self.__if_branch

    def get_else_branch(self) -> ListOfRules:
        return self.__else_branch

    def get_condition(self) -> Condition:
        return self.__condition

    def _execute(self, instance: Instance, sequence: Tuple[str]):
        if self.__condition.check_instance(instance):
            self.__if_branch._execute(instance, sequence)
        else:
            self.__else_branch._execute(instance, sequence)

    def _execute_with_backtrace(
            self, parent: 'ListOfRules', index: int, instance: Instance,
            sequence: List[str], backtrace: Backtrace):
        if self.__condition.check_instance(instance):
            self.__if_branch._execute_with_backtrace(
                self, 0, instance, sequence, backtrace)
        else:
            self.__else_branch._execute_with_backtrace(
                self, 1, instance, sequence, backtrace)

    def compute_mdl(self, set_of_symbols: Set[str],
                    nr_of_attributes: int) -> float:
        mdl = self.__condition.compute_mdl(nr_of_attributes)
        mdl += self.__if_branch.compute_mdl(set_of_symbols, nr_of_attributes)
        mdl += self.__else_branch.compute_mdl(set_of_symbols, nr_of_attributes)
        return mdl

    def estimate_counter_change(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        """
        optimistically estimates how the edits_counter will change for the
        given instance if this rule is added to the model
        """
        if self.__condition.check_instance(instance):
            self.__if_branch.estimate_counter_change(
                edits_counter, missing_symbols_counter, instance)
        else:
            self.__else_branch.estimate_counter_change(
                edits_counter, missing_symbols_counter, instance)

    def estimate_counter_change_on_remove(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        """
        optimistically estimates how the edits_counter will change for the
        given instance if this rule is added to the model
        """
        if self.__condition.check_instance(instance):
            self.__if_branch.estimate_counter_change_on_remove(
                edits_counter, missing_symbols_counter, instance)
        else:
            self.__else_branch.estimate_counter_change_on_remove(
                edits_counter, missing_symbols_counter, instance)

    def __get_estimate_relevant_dataset_split(self,
            instances: List[Instance]) -> Tuple[List[Instance], List[Instance]]:
        if_branch = []
        else_branch = []
        for instance in instances:
            if self.__condition.check_instance(instance):
                if_branch.append(instance)
            elif len(self.__else_branch) > 1:
                else_branch.append(instance)
        return if_branch, else_branch

    def compute_fast_data_mdl_gain_estimate_for_insert(
            self, instances: List[Instance], alphabet_size: int) -> float:
        if_branch, else_branch = self.__get_estimate_relevant_dataset_split(instances)
        estimated_gain = self.__if_branch.compute_fast_data_mdl_gain_estimate_for_insert(
            if_branch, alphabet_size
        )
        if else_branch:
            estimated_gain += self.__else_branch.compute_fast_data_mdl_gain_estimate_for_insert(
                else_branch, alphabet_size)
        return estimated_gain

    def compute_fast_data_mdl_gain_estimate_for_delete(
            self, instances: List[Instance]) -> float:
        if_branch, else_branch = self.__get_estimate_relevant_dataset_split(instances)
        estimated_gain = self.__if_branch.compute_fast_data_mdl_gain_estimate_for_delete(
            if_branch
        )
        if else_branch:
            estimated_gain += self.__else_branch.compute_fast_data_mdl_gain_estimate_for_delete(
                else_branch)
        return estimated_gain

    def yield_subrules(self) -> Generator['Rule', None, None]:
        yield self.__if_branch
        yield self.__else_branch
        yield from self.__if_branch.yield_subrules()
        yield from self.__else_branch.yield_subrules()

    def get_appendable_symbols(self) -> Set[str]:
        appendable_symbols = set()
        appendable_symbols.update(self.__if_branch.get_appendable_symbols())
        appendable_symbols.update(self.__else_branch.get_appendable_symbols())
        return appendable_symbols

    def count_nr_of_terms(self) -> int:
        nr_of_terms = self.__condition.count_nr_of_terms()
        nr_of_terms += self.__if_branch.count_nr_of_terms()
        nr_of_terms += self.__else_branch.count_nr_of_terms()
        return nr_of_terms

    def to_string(self, prefix='') -> str:
        s = '%sIF %s THEN\n%s' % (prefix, str(self.__condition),
                                self.__if_branch.to_string(prefix + '  '))
        if len(self.__else_branch) > 0:
            s += '\n%sELSE\n%s' % (prefix,
                                   self.__else_branch.to_string(prefix + '  '))
        return s

    def to_html(self) -> str:
        return ('<div class="Rule IfThenElseRule">'
                '<div class="If">If</div>'
                '%s'
                '<div class="ifbranch">%s</div>'
                '%s'
                '<div class="elsebranch">%s</div>'
                '</div>') % (
                    self.__condition.to_html(),
                    self.__if_branch.to_html(),
                    '<div class="Else">Else</div>' if len(self.__else_branch) > 0 else '',
                    self.__else_branch.to_html()
                )

    def _add_to_digraph(self, graph: Digraph) -> List[str]:
        graph.node(str(id(self)), label=str(self.__condition), shape='rectangle')
        end_ids = self.__if_branch._add_to_digraph(graph)
        graph.edge(str(id(self)), str(id(self.__if_branch[0])), label='yes')
        if len(self.__else_branch) > 0:
            graph.edge(str(id(self)), str(id(self.__else_branch[0])))
            end_ids.extend(self.__else_branch._add_to_digraph(graph))
        else:
            end_ids.append(str(id(self)))
        return end_ids

    def _add_to_eventflow_graph(
            self, preceding_nodes: List[Node], next_nodes: List[Node],
            graph: EventFlowGraph) -> Tuple[List[Node], List[Node]]:
        source_nodes, sink_nodes = self.__if_branch._add_to_eventflow_graph(
            preceding_nodes, next_nodes, graph)
        else_source_nodes, else_sink_nodes = self.__else_branch._add_to_eventflow_graph(
            preceding_nodes, next_nodes, graph)
        if else_source_nodes:
            source_nodes.extend(else_source_nodes)
            sink_nodes.extend(else_sink_nodes)
        else:
            sink_nodes.extend(preceding_nodes)
        return source_nodes, sink_nodes

    @staticmethod
    def create_and_set_subdatasets(
            condition: Condition, literal: RuleLiteral,
            subdataset: Dataset) -> 'IfThenElseRule':
        candidate = IfThenElseRule(condition)
        candidate.get_if_branch().append_rule(literal)
        if_instances = []
        else_instances = []
        for instance in subdataset:
            if condition.check_instance(instance):
                if_instances.append(instance)
            else:
                else_instances.append(instance)
        candidate.get_if_branch().set_subdataset_supplier(
                lambda: subdataset.get_subdataset(if_instances))
        candidate.get_else_branch().set_subdataset_supplier(
                lambda: subdataset.get_subdataset(else_instances))
        return candidate
