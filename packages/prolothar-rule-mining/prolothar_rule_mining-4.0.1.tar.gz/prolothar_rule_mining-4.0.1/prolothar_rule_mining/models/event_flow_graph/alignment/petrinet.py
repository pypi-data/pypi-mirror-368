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
from typing import Union, List, Tuple

from pm4py.algo.conformance.alignments.petri_net.variants.dijkstra_no_heuristics import apply as compute_alignment_with_pm4py
from pm4py.objects.log.obj import Trace as Pm4PyTrace
from pm4py.objects.log.obj import Event as Pm4PyEvent
from prolothar_rule_mining.models.converter.eventflow_graph_to_pm4py_petrinet_converter import EventFlowGraphToPm4pyPetrinetConverter

from prolothar_rule_mining.models.event_flow_graph.alignment.alignment import Alignment
from prolothar_rule_mining.models.event_flow_graph.alignment.alignment_finder import AlignmentFinder

class PetrinetAligner(AlignmentFinder):
    """
    converts the EventFlowGraph to a petrinet and uses existing alignment algorithms
    """

    def compute_alignment(self, sequence: Union[List[str], Tuple[str]]) -> Alignment:
        trace = Pm4PyTrace([Pm4PyEvent({'concept:name': event}) for event in sequence])

        petri_net, initial_marking, final_marking = EventFlowGraphToPm4pyPetrinetConverter(
            ).convert(self.graph)
        pm4py_alignment = compute_alignment_with_pm4py(trace, petri_net, initial_marking, final_marking, parameters={'ret_tuple_as_trans_desc': True})

        alignment = Alignment()

        event_index = 0
        for move in pm4py_alignment['alignment'][1:-1]:
            transition_name_tracenet, transition_name_model = move[0]
            transition_label_tracenet, transition_label_model = move[1]
            if transition_label_tracenet == transition_label_model:
                alignment.append_sync_move(
                    self.graph.get_node_by_id(int(transition_name_model)), event_index)
                event_index += 1
            elif transition_name_tracenet != '>>':
                alignment.append_log_move(event_index)
                event_index += 1
            elif transition_label_model is not None:
                alignment.append_model_move(self.graph.get_node_by_id(
                    int(transition_name_model)))

        #make sure the complete sequence is covered
        for i in range(event_index, len(sequence)):
            alignment.append_log_move(i)

        alignment.append_sync_move(self.graph.sink, len(sequence))

        return alignment
