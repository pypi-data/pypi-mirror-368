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
from typing import Union

from prolothar_common.models.eventlog import EventLog, Trace

class MajorityEventPredictor:
    """
    always predicts the most frequent event in the trainset as the next event
    """

    def __init__(self):
        self.__majority_class: Union[str, None] = None

    def train(self, eventlog: EventLog):
        activity_supports = eventlog.compute_activity_supports()
        self.__majority_class = max(activity_supports.items(), key=lambda x: x[1])[0]

    def predict(self, prefix_trace: Trace) -> str:
        return self.__majority_class
