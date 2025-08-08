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
this module contains the ModelCodeCounter class
"""

from typing import Generator

class ModelCodeCounter:
    """
    counts how many missed, redundant and matched events are present in the cover
    """

    __slots__ = ('missed_events', 'redundant_events', 'matched_events')

    def __init__(self):
        self.missed_events: int = 0
        self.redundant_events: int = 0
        self.matched_events: int = 0

    def __eq__(self, other: 'ModelCodeCounter'):
        return (self.missed_events == other.missed_events
            and self.redundant_events == other.redundant_events
            and self.matched_events == other.matched_events)

    def __repr__(self) -> str:
        return '{missed_events: %d, redundant_events: %d, matched_events: %d}' % (
            self.missed_events, self.redundant_events, self.matched_events
        )

    def __len__(self) -> int:
        """
        this is used in prolothar_common_mdl_utils to compute the prequential
        coding length of this dictionary like structure. "3" is the number of
        different codes (missed, redundant, matched).
        """
        return 3

    def values(self) -> Generator[int,None,None]:
        yield self.missed_events
        yield self.redundant_events
        yield self.matched_events

    def add(self, other: 'ModelCodeCounter'):
        """
        adds the counts of another ModelCodeCounter
        """
        self.missed_events += other.missed_events
        self.redundant_events += other.redundant_events
        self.matched_events += other.matched_events