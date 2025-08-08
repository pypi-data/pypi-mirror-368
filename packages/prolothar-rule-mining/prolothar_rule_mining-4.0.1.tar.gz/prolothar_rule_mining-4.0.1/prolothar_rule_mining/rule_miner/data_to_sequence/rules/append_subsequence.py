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
from prolothar_common.collections import list_utils
from prolothar_common.levenshtein import EditOperationType
import prolothar_common.mdl_utils as mdl_utils
from prolothar_common.models.dataset.instance import Instance

from prolothar_rule_mining.rule_miner.data_to_sequence.rules.rule_literal import RuleLiteral
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.append_rule import AppendRule
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node

class AppendSubsequenceRule(RuleLiteral):
    """appends a subsequence to a sequence"""

    def __init__(self, subsequence: List[str]):
        self.__subsequence = subsequence

    def __eq__(self, other) -> bool:
        try:
            return self.__subsequence == other.__subsequence
        except AttributeError:
            return False

    def __hash__(self) -> int:
        value = 0
        for symbol in self.__subsequence:
            value = value ^ hash(symbol)
        return value

    def _execute(self, instance: Instance, sequence: Tuple[str]):
        sequence.extend(self.__subsequence)

    def compute_mdl(self, set_of_symbols: Set[str],
                    nr_of_attributes: int) -> float:
        return mdl_utils.L_N(len(self.__subsequence)) + (
            len(self.__subsequence) * log2(len(set_of_symbols)))

    def estimate_counter_change(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        for symbol in self.__subsequence:
            AppendRule(symbol).estimate_counter_change(
                edits_counter, missing_symbols_counter, instance)

    def estimate_counter_change_on_remove(
            self, edits_counter: Dict[EditOperationType, int],
            missing_symbols_counter: Dict[str, int],
            instance: Instance) -> Dict[EditOperationType, int]:
        for symbol in self.__subsequence:
            AppendRule(symbol).estimate_counter_change_on_remove(
                edits_counter, missing_symbols_counter, instance)

    def compute_fast_data_mdl_gain_estimate_for_insert(
            self, instances: List[Instance], alphabet_size: int) -> float:
        estimated_gain = 0
        for symbol in self.__subsequence:
            estimated_gain += AppendRule(
                symbol).compute_fast_data_mdl_gain_estimate_for_insert(
                    instances, alphabet_size)
        return estimated_gain

    def compute_fast_data_mdl_gain_estimate_for_delete(
            self, instances: List[Instance]) -> float:
        estimated_gain = 0
        for symbol in self.__subsequence:
            estimated_gain += AppendRule(
                symbol).compute_fast_data_mdl_gain_estimate_for_delete(
                    instances)
        return estimated_gain

    def appears_in_sequence(self, sequence: Tuple[str]) -> bool:
        return list_utils.is_sublist_bm(sequence, self.__subsequence)

    def get_sequence(self) -> List[str]:
        return self.__subsequence

    def get_appendable_symbols(self) -> Set[str]:
        return set(self.__subsequence)

    def _add_to_eventflow_graph(
            self, preceding_nodes: List[Node], next_nodes: List[Node],
            graph: EventFlowGraph) -> Tuple[List[Node], List[Node]]:
        nodes = []
        for symbol in self.__subsequence:
            nodes.append(graph.add_node(symbol))
        for preceding_node in preceding_nodes:
            graph.add_edge(preceding_node, nodes[0])
        for next_node in next_nodes:
            graph.add_edge(nodes[0], next_node)
        return [nodes[0]], [nodes[-1]]

    def to_string(self, prefix='') -> str:
        return '%sAppend Sequence [%s]' % (prefix, ','.join(self.__subsequence))

    def to_html(self) -> str:
        return '<div class="Rule AppendSubsequenceRule">%s</div>' % ', '.join(
            self.__subsequence)