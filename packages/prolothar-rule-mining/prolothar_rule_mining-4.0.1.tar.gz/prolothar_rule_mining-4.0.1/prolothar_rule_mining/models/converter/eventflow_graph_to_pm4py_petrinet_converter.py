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

from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.petri_net.obj import Marking

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph

class EventFlowGraphToPm4pyPetrinetConverter():
    """
    converts an EventFlowGraph to a pm4py PetriNet
    """

    def convert(self, graph: EventFlowGraph) -> Tuple[PetriNet, Marking, Marking]:
        """
        converts an EventFlowGraph to a pm4py PetriNet and returns the Petrinet,
        initial marking and final marking
        """
        petri_net = PetriNet()
        pre_place_dict = {}
        post_place_dict = {}

        source_place = PetriNet.Place('source')
        petri_net.places.add(source_place)
        post_place_dict[graph.source] = source_place

        sink_place = PetriNet.Place('sink')
        petri_net.places.add(sink_place)
        pre_place_dict[graph.sink] = sink_place

        for node in graph.nodes():
            pre_place = PetriNet.Place('pre_' + str(node.node_id))
            pre_place_dict[node] = pre_place
            post_place = PetriNet.Place('post_' + str(node.node_id))
            post_place_dict[node] = post_place
            transition = PetriNet.Transition(str(node.node_id), node.event)
            petri_net.transitions.add(transition)
            petri_net.places.add(pre_place)
            petri_net.places.add(post_place)
            petri_utils.add_arc_from_to(pre_place, transition, petri_net)
            petri_utils.add_arc_from_to(transition, post_place, petri_net)

        for edge in graph.edges():
            transition = PetriNet.Transition(
                '%d_%d' % (edge.from_node.node_id, edge.to_node.node_id), None)
            petri_net.transitions.add(transition)
            petri_utils.add_arc_from_to(post_place_dict[edge.from_node], transition, petri_net)
            petri_utils.add_arc_from_to(transition, pre_place_dict[edge.to_node], petri_net)

        initial_marking = Marking()
        initial_marking[post_place_dict[graph.source]] = 1
        final_marking = Marking()
        final_marking[pre_place_dict[graph.sink]] = 1

        return petri_net, initial_marking, final_marking

