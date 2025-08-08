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
from typing import List, Union

from collections import defaultdict

from prolothar_common.levenshtein cimport compute_cost_matrix, backtrace
from prolothar_common.levenshtein cimport EditOperationType, EditOperation

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment import Alignment
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment cimport Alignment as CAlignment
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder cimport AlignmentFinder

cdef extern from "limits.h":
    cdef int INT_MAX

cdef (int, int) edit_operation_sort(EditOperation e):
    return (e.i,e.j)

cdef class PathEnumeration(AlignmentFinder):
    """
    enumerates all possible paths on the graph and for each path computes an
    alignment with a given sequence to find the best one. a simple lower bound
    heuristic on the length difference of the model and data sequence prunes
    the search space.
    """

    cdef list all_paths

    def __init__(self, graph: EventFlowGraph):
        super().__init__(graph)
        self.all_paths = []
        open_paths = [[node] for node in self.graph.source.children]
        while open_paths:
            path = open_paths.pop()
            if path[-1] is self.graph.sink:
                self.all_paths.append(path[:-1])
            else:
                children = iter(path[-1].children)
                path.append(next(children))
                open_paths.append(path)
                while True:
                    try:
                        open_paths.append(path[:-1] + [next(children)])
                    except StopIteration:
                        break

    def compute_alignment(self, sequence: Tuple[str]) -> Alignment:
        cdef int best_cost = INT_MAX
        cdef int[:,:] best_cost_matrix
        cdef int[:,:] path_cost_matrix
        cdef int path_cost

        events_in_sequence = defaultdict(int)
        for event in sequence:
            events_in_sequence[event] += 1

        all_paths_with_heuristic = [
            (self.__compute_lower_bound(path, sequence, events_in_sequence), path)
            for path in self.all_paths
        ]
        all_paths_with_heuristic.sort(key=lambda x: x[0])

        best_path = None
        for path_lower_bound,path in all_paths_with_heuristic:
            if path_lower_bound < best_cost:
                path_cost_matrix = compute_cost_matrix(
                    [node.event for node in path], sequence,
                    substitution_cost=2, insertion_cost=1, deletion_cost=1)
                path_cost = path_cost_matrix[-1,-1]
                if path_cost < best_cost:
                    best_cost = path_cost
                    best_path = path
                    best_cost_matrix = path_cost_matrix
            else:
                break

        return self.__create_alignment(best_path, sequence, best_cost_matrix)

    def __compute_lower_bound(
            self, path: List[Node], sequence: Tuple[str], events_in_sequence) -> int:
        events_in_path = defaultdict(int)
        for node in path:
            events_in_path[node.event] += 1
        for event, count in events_in_sequence.items():
            events_in_path[event] -= count
        heuristic_on_events = 0
        for count_difference in events_in_path.values():
            heuristic_on_events += abs(count_difference)
        return max(abs(len(path) - len(sequence)), heuristic_on_events)

    cpdef CAlignment __create_alignment(self, list best_path, sequence: Union[list,tuple],
                             int[:,:] best_cost_matrix):
        cdef CAlignment alignment = CAlignment()
        cdef int model_index = 0
        cdef int sequence_index = 0
        for edit_operation in sorted(
                backtrace(best_path, sequence, best_cost_matrix),
                key=edit_operation_sort):
            for i in range(model_index, edit_operation.i):
                alignment.append_sync_move(best_path[i], sequence_index)
                sequence_index += 1
            model_index = edit_operation.i
            sequence_index = edit_operation.j
            if edit_operation.operation_type == EditOperationType.DELETE:
                alignment.append_model_move(best_path[edit_operation.i])
                model_index += 1
            elif edit_operation.operation_type == EditOperationType.INSERT:
                alignment.append_log_move(edit_operation.j)
                sequence_index += 1
            else:
                alignment.append_model_move(best_path[edit_operation.i])
                alignment.append_log_move(edit_operation.j)
                model_index += 1
                sequence_index += 1
        for i in range(model_index, len(best_path)):
            alignment.append_sync_move(best_path[i], sequence_index)
            sequence_index += 1
        alignment.append_sync_move(self.graph.sink, len(sequence))
        return alignment

