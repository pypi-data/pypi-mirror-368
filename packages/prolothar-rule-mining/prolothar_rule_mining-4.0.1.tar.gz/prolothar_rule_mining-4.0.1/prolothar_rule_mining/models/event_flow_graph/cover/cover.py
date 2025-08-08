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
this module contains the cover model
"""

from typing import Dict, Set, Tuple, List, Union

from abc import ABC, abstractmethod

from collections import defaultdict
from itertools import chain

from prolothar_common import mdl_utils

from prolothar_rule_mining.models.event_flow_graph.graph import Node
from prolothar_rule_mining.models.event_flow_graph.cover.model_code_counter import ModelCodeCounter

class CoverStep(ABC):
    """
    one step in the cover
    """

    def __init__(self, cover: 'Cover', current_node: Node, event: str):
        self.current_node = current_node
        self.event = event
        self.cover = cover

    @abstractmethod
    def execute(self):
        """
        adds this step to the given cover
        """

    @abstractmethod
    def undo(self):
        """
        removes this step from the given cover
        """

    def __repr__(self) -> str:
        return '(%r,%r)' % (self.current_node, self.event)

class MissedEventCoverStep(CoverStep):

    def execute(self):
        self.cover.model_codes[self.current_node].missed_events += 1
        self.cover.missed_event_codes[self.current_node][self.event] += 1

    def undo(self):
        self.cover.model_codes[self.current_node].missed_events -= 1
        self.cover.missed_event_codes[self.current_node][self.event] -= 1

class RedundantEventCoverStep(CoverStep):

    def execute(self):
        self.cover.model_codes[self.current_node].redundant_events += 1
        try:
            self.cover.redundant_event_codes[self.current_node][self.event] += 1
        except KeyError:
            counter = {child.event: 0 for child in self.current_node.children}
            counter[self.event] = 1
            self.cover.redundant_event_codes[self.current_node] = counter

    def undo(self):
        self.cover.model_codes[self.current_node].redundant_events -= 1
        self.cover.redundant_event_codes[self.current_node][self.event] -= 1

class MatchedEventCoverStep(CoverStep):

    def execute(self):
        self.cover.model_codes[self.current_node].matched_events += 1
        try:
            self.cover.matched_event_codes[self.current_node][self.event] += 1
        except KeyError:
            counter = {child.event: 0 for child in self.current_node.children}
            counter[self.event] = 1
            self.cover.matched_event_codes[self.current_node] = counter

    def undo(self):
        self.cover.model_codes[self.current_node].matched_events -= 1
        try:
            self.cover.matched_event_codes[self.current_node][self.event] -= 1
        except KeyError as e:
            print(self.current_node)
            print(self.cover.matched_event_codes[self.current_node])
            raise e

class Cover:
    """
    the model of a cover of a given dataset by a given EventFlowGraph
    """

    def __init__(self, event_alphabet: Set[str], end_of_sequence_symbol: str):
        self.model_codes: Dict[Node, ModelCodeCounter] = defaultdict(ModelCodeCounter)
        self.missed_event_codes: Dict[Node, Dict[str, int]] = defaultdict(
            lambda: {
                event: 0 for event in chain(event_alphabet, [end_of_sequence_symbol])
            }
        )
        self.redundant_event_codes: Dict[Node, Dict[str, int]] = {}
        self.matched_event_codes: Dict[Node, Dict[str, int]] = {}
        self.__sequence_cache: Dict[Tuple[str], List[CoverStep]] = {}
        self.__steps_for_current_sequence: List[CoverStep] = []
        self.__current_sequence: Union[None, Tuple[str]] = None

    def start_recording_for_sequence(self, sequence: Tuple[str]):
        """
        sets the current sequence. in the following, all operations on the cover
        are recorded, such that latern for a given sequence we can repeat or
        undo the steps. the method "end_recording_for_sequence()" stops the
        recording and makes the recording available.
        """
        self.__current_sequence = sequence

    def end_recording_for_sequence(self):
        """
        sets the current sequence. in the following, all operations on the cover
        are recorded, such that latern for a given sequence we can repeat or
        undo the steps. the method "end_recording_for_sequence()" stops the
        recording and makes the recording available.
        """
        self.__sequence_cache[self.__current_sequence] = self.__steps_for_current_sequence
        self.__current_sequence = None
        self.__steps_for_current_sequence = []

    def get_steps_for_sequence(self, sequence: Tuple[str]) -> List[CoverStep]:
        """
        retrieves the CoverSteps for a given sequence. If not available, a
        a KeyError is raised. A sequence is available if it has been recorded
        with "start_recording_for_sequence" and "end_recording_for_sequence".
        """
        return self.__sequence_cache[sequence]

    def set_steps_for_sequence(
        self, steps: List[CoverStep], sequence: Tuple[str]) -> List[CoverStep]:
        """
        sets the CoverSteps for a given sequence for future lookups with
        "get_steps_for_sequence".
        """
        self.__sequence_cache[sequence] = steps

    def clear_steps_for_sequence(self, sequence: Tuple[str]) -> List[CoverStep]:
        """
        retrieves the CoverSteps for a given sequence. If not available, a
        a KeyError is raised. A sequence is available if it has been recorded
        with "start_recording_for_sequence" and "end_recording_for_sequence".
        """
        self.__sequence_cache.pop(sequence)

    def __add_step(self, step: CoverStep):
        step.execute()
        if self.__current_sequence is not None:
            self.__steps_for_current_sequence.append(step)

    def add_missed_event(self, current_node: Node, missed_event: str):
        self.__add_step(MissedEventCoverStep(self, current_node, missed_event))

    def add_redundant_event(self, current_node: Node, redundant_event: str):
        self.__add_step(RedundantEventCoverStep(self, current_node, redundant_event))

    def add_matched_event(self, current_node: Node, matched_event: str):
        self.__add_step(MatchedEventCoverStep(self, current_node, matched_event))

    def count_model_codes(self) -> ModelCodeCounter:
        result = ModelCodeCounter()
        for counter in self.model_codes.values():
            result.add(counter)
        return result

    def compute_mdl(self, v=False) -> float:
        mdl = 0
        model_counter_dict = {0: 0, 1: 0, 2: 0}
        for counter in self.model_codes.values():
            model_counter_dict[0] = counter.matched_events
            model_counter_dict[1] = counter.missed_events
            model_counter_dict[2] = counter.redundant_events
            mdl += mdl_utils.prequential_coding_length(model_counter_dict)
        for counter in self.missed_event_codes.values():
            mdl += mdl_utils.prequential_coding_length(counter)
        for counter in self.redundant_event_codes.values():
            mdl += mdl_utils.prequential_coding_length(counter)
        for counter in self.matched_event_codes.values():
            mdl += mdl_utils.prequential_coding_length(counter)
        return mdl
