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

from typing import Callable

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.func_tools import do_nothing

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph.alignment.petrinet import PetrinetAligner

from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.event_flow_graph_miner.abstract import EventFlowGraphMiner
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.candidates import AddSequencePathCandidate

class SequenceAlignmentNoMdl(EventFlowGraphMiner):
    """
    similar to SequenceBottomUpEventFlowGraphMiner but without using MDL to
    decide when to stop
    """

    def __init__(self, logger: Callable[[str], None] = print):
        """
        creates a new EventFlowGraphMiner
        """
        self.__logger = logger if logger is not None else do_nothing

    def mine_event_flow_graph(self, dataset: TargetSequenceDataset) -> EventFlowGraphMiner:
        graph = EventFlowGraph()

        all_sequences = dataset.get_sequences_ordered_by_frequency()
        for i,sequence in enumerate(reversed(all_sequences)):
            self.__logger(f'extend model for sequence {i+1} of {len(all_sequences)}')
            AddSequencePathCandidate(
                graph, sequence, alignment_finder=PetrinetAligner(graph)).apply()

        graph.merge_redundant_nodes()

        return graph

    def __repr__(self) -> str:
        return 'SequenceAlignmentNoMdl()'