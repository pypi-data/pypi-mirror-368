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
this module contains an Oracle event flow graph miner, i.e. for a given dataset a
already specified event flow graph (e.g. the true model generating the data) is
returned
"""

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph

from prolothar_common.models.dataset import TargetSequenceDataset

from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.event_flow_graph_miner.abstract import EventFlowGraphMiner

class OracleEventFlowGraphMiner(EventFlowGraphMiner):
    """
    for a given dataset a
    already specified event flow graph (e.g. the true model generating the data) is
    returned
    """

    def __init__(self, event_flow_graph: EventFlowGraph):
        """
        creates a new EventFlowGraphMiner
        """
        self.__event_flow_graph = event_flow_graph

    def mine_event_flow_graph(self, dataset: TargetSequenceDataset) -> EventFlowGraphMiner:
        return self.__event_flow_graph

    def __repr__(self) -> str:
        return 'OracleEventFlowGraphMiner()'