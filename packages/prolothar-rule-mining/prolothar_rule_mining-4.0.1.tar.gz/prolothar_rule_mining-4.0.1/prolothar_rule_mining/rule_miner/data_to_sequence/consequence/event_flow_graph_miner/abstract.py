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
this module contains the event flow graph miner, i.e. for a given dataset an
event flow graph is inferred
"""

from abc import ABC, abstractmethod

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph

class EventFlowGraphMiner(ABC):
    """
    infers an EventFlowGraph from a given sequential dataset.
    """

    @abstractmethod
    def mine_event_flow_graph(self, dataset: TargetSequenceDataset) -> EventFlowGraph:
        """
        infers an EventFlowGraph from a given sequential dataset.
        """
