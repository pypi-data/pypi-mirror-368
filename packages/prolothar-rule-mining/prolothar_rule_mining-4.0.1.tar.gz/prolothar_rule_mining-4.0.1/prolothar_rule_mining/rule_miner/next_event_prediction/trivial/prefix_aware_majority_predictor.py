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
from typing import Union, Dict, Tuple
from collections import defaultdict

from prolothar_common.models.eventlog import EventLog, Trace

from prolothar_rule_mining.rule_miner.next_event_prediction.trivial.majority_event_predictor import MajorityEventPredictor
from prolothar_rule_mining.rule_miner.next_event_prediction.eventlog_iterator import eventlog_iterator

class PrefixAwareMajorityPredictor:
    """
    for known prefixes from the training set, predicts the most frequent seen
    next event.
    for unknown prefixes predicts the most frequent event overall in the trainset
    """

    def __init__(self):
        self.__majority_event_predictor: Union[MajorityEventPredictor, None] = None
        self.__majority_event_per_prefix: Union[Dict[Tuple[str], str], None] = None

    def train(self, eventlog: EventLog):
        self.__majority_event_predictor = MajorityEventPredictor()
        self.__majority_event_predictor.train(eventlog)

        event_counter_per_prefix = defaultdict(lambda: defaultdict(int))

        for prefix, next_event in eventlog_iterator(eventlog):
            event_counter_per_prefix[tuple(prefix.to_activity_list())][next_event] += 1

        self.__majority_event_per_prefix = {}
        for prefix, event_counter in event_counter_per_prefix.items():
            self.__majority_event_per_prefix[prefix] = max(event_counter.items(), key=lambda x: x[1])[0]

    def predict(self, prefix_trace: Trace) -> str:
        return self.__majority_event_per_prefix.get(
            tuple(prefix_trace.to_activity_list()),
            self.__majority_event_predictor.predict(prefix_trace))
