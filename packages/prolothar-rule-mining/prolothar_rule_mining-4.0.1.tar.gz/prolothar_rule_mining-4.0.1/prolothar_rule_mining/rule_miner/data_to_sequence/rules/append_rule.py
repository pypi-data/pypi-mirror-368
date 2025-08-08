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
from typing import List, Set, Dict, Tuple

from math import log2
from prolothar_common.levenshtein import EditOperationType
from prolothar_common.models.dataset.instance import Instance

from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule_literal import RuleLiteral
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node

class AppendRule(RuleLiteral):
    """appends a symbol to a sequence"""

    def __init__(self, symbol: str):
        super().__init__()
        self.__symbol = symbol

    def get_symbol(self) -> str:
        return self.__symbol

    def __eq__(self, other) -> bool:
        try:
            return self.__symbol == other.__symbol
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return hash(self.__symbol)

    def _execute(self, instance: Instance, sequence: Tuple[str]):
        sequence.append(self.__symbol)

    def compute_mdl(self, set_of_symbols: Set[str],
                    nr_of_attributes: int) -> float:
        return log2(len(set_of_symbols))

    def estimate_counter_change(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        if missing_symbols_counter[self.__symbol] > 0:
            missing_symbols_counter[self.__symbol] -= 1
            if edits_counter[EditOperationType.INSERT] > 0:
                edits_counter[EditOperationType.INSERT] -= 1
        else:
            edits_counter[EditOperationType.DELETE] += 1

    def estimate_counter_change_on_remove(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        if self.__symbol in instance.get_target_sequence():
            missing_symbols_counter[self.__symbol] += 1
        if edits_counter[EditOperationType.DELETE] > 0:
            edits_counter[EditOperationType.DELETE] -= 1

    def compute_fast_data_mdl_gain_estimate_for_insert(
            self, instances: List[Instance], alphabet_size: int) -> float:
        estimated_gain = 0
        for instance in instances:
            if instance.contains_symbol(self.__symbol):
                #optimistic estimate: one element less to insert
                estimated_gain += (
                    log2(len(instance.get_target_sequence()) + 1) +
                    log2(alphabet_size)
                )
        return estimated_gain

    def compute_fast_data_mdl_gain_estimate_for_delete(
            self, instances: List[Instance]) -> float:
        estimated_gain = 0
        for instance in instances:
            #optimistic estimate: one element less to delete
            estimated_gain += log2(len(instance.get_target_sequence()))
        return estimated_gain

    def appears_in_sequence(self, sequence: Tuple[str]) -> bool:
        return self.__symbol in sequence

    def get_appendable_symbols(self) -> Set[str]:
        return set([self.__symbol])

    def _add_to_eventflow_graph(
            self, preceding_nodes: List[Node], next_nodes: List[Node],
            graph: EventFlowGraph) -> Tuple[List[Node], List[Node]]:
        node = graph.add_node(self.__symbol)
        for preceding_node in preceding_nodes:
            graph.add_edge(preceding_node, node)
        for next_node in next_nodes:
            graph.add_edge(node, next_node)
        return [node], [node]

    def to_string(self, prefix='') -> str:
        return '%sAppend %r' % (prefix, self.__symbol)

    def to_html(self) -> str:
        return '<div id="%d" class="Rule AppendRule">%s</div>' % (
            id(self), self.__symbol)