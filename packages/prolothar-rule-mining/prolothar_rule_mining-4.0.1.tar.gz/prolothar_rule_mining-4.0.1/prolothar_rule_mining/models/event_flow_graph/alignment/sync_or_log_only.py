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
from typing import Tuple

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment import Alignment
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder import AlignmentFinder

class SyncOrLogOnly(AlignmentFinder):
    """
    requires a direct edge from source to sink. either a sequence can be
    explained with synchronous moves only or the complete sequence is modeled
    with log moves, such that there are not model moves in the alignment
    """

    def __init__(self, graph: EventFlowGraph):
        super().__init__(graph)
        if graph.sink not in graph.source.children:
            raise ValueError('source and sink must have a direct edge')

    def compute_alignment(self, sequence: Tuple[str]) -> Alignment:
        candidates = [Alignment()]
        event_index = 0
        while candidates:
            if event_index <= len(sequence):
                try:
                    event = sequence[event_index]
                except IndexError:
                    event = self.graph.sink.event
                new_candidates = []
                for candidate in candidates:
                    new_candidates.extend(self.__extend_candidate(
                        candidate, event_index, event))
                candidates = new_candidates
                event_index += 1
            else:
                return candidates.pop()

        #no perfect synchronous alignment could be found => use log moves only
        alignment = Alignment()
        for i,_ in enumerate(sequence):
            alignment.append_log_move(i)
        alignment.append_sync_move(self.graph.sink, len(sequence))
        return alignment

    def __extend_candidate(self, candidate: Alignment, event_index: int, event: str):
        if len(candidate) == 0:
            node = self.graph.source
        else:
            node = candidate.get_last_move().node

        for next_node in node.children:
            if next_node.event == event:
                extencded_candidate = candidate.copy()
                extencded_candidate.append_sync_move(next_node, event_index)
                yield extencded_candidate
