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
from typing import List

import heapq

from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates.candidate import Candidate


class CandidateQueue:
    """
    a priority queue of the candidates
    """

    def __init__(self):
        self.__queue: List[Candidate] = []

    def add(self, candidate: Candidate):
        """
        adds the candidate to this queue
        """
        heapq.heappush(self.__queue, candidate)

    def pop(self) -> Candidate:
        """
        pops the candidate with the lowest priority
        """
        return heapq.heappop(self.__queue)

    def is_not_empty(self) -> bool:
        """
        returns True if there are still elements in this queue, otherwise False
        """
        return bool(self.__queue)

    def __len__(self) -> int:
        """
        returns the length (the number of candidates) in this queue
        """
        return len(self.__queue)
