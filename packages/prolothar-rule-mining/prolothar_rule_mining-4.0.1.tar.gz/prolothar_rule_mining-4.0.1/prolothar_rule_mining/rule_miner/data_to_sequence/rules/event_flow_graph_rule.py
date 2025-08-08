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
from typing import List, Dict, Callable, Any
import sys

import lxml.builder
import lxml.etree

from prolothar_common.func_tools import identity

from prolothar_common.models.dataset.instance import Instance
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node
from prolothar_rule_mining.models.event_flow_graph.router.router import Router
from prolothar_rule_mining.models.event_flow_graph.router.ruled_router import RuledRouter

class EventFlowGraphRule():
    """
    uses an EventFlowGraph to generate sequences fromm instances. This kind of
    rule uses so-called routers to decide which branch to follow in the graph
    whenever the current node has more than one child.
    """

    def __init__(self, event_flow_graph: EventFlowGraph,
                 node_router_table: Dict[Node, Router]):
        self.__event_flow_graph: EventFlowGraph = event_flow_graph
        self.__node_router_table = node_router_table

    def execute(
        self, instance: Instance,
        add_nr_of_instances_to_edges: bool = False) -> List[str]:
        """
        generates a sequence from the given instance

        Parameters
        ----------
        instance : Instance
            contains attributes that are used to decide for routing in the graph
        add_nr_of_instances_to_edges : bool, optional
            if True, then adds edge.attributes['nr_of_instances'], by default False

        Returns
        -------
        List[str]
            the generated sequence
        """
        sequence = []
        node = self.__event_flow_graph.source
        while node != self.__event_flow_graph.sink:
            last_node = node
            sequence.append(node.event)
            if len(node.children) == 1:
                node = next(iter(node.children))
            else:
                try:
                    node = self.__node_router_table[node](instance)
                except KeyError:
                    self.__event_flow_graph.plot(show=False, with_node_ids=True, filepath='temp')
                    raise NotImplementedError((node, len(node.children), self.__event_flow_graph.get_node_by_id(node.node_id).children))

            if add_nr_of_instances_to_edges:
                self.__event_flow_graph.get_edge(
                    last_node, node).attributes['nr_of_instances'] += 1

        #we do not emit the source symbol
        return sequence[1:]

    def get_node_router_table(self) -> Dict[Node, Router]:
        return self.__node_router_table

    def get_event_flow_graph(self) -> EventFlowGraph:
        return self.__event_flow_graph

    def count_nr_of_terms(self) -> int:
        nr_of_terms = 0
        for router in self.__node_router_table.values():
            if isinstance(router, RuledRouter):
                nr_of_terms += router.get_rule().count_nr_of_terms()
            else:
                raise NotImplementedError('at least one router is a blackbox of type %r' % router)
        return nr_of_terms

    def get_nr_of_nodes(self) -> int:
        return self.__event_flow_graph.get_nr_of_nodes()

    def to_odm_xml(
        self, stop_action: str = 'return sequence',
        action_format: str = 'add "%s" to sequence',
        attribute_formatter: Callable[[str], str] = identity,
        operator_formatter: Callable[[str], str] = identity,
        join_operator_formatter: Callable[[str], str] = identity,
        numerical_value_formatter: Callable[[float], str] = str,
        categorical_value_formatter: Callable[[Any], str] = str) -> str:
        """
        generates the <Body> tag of a IBM ODM RuleFlow.
        current implementation does only work for first firing rules without
        nested rules and with a default rule at the end of the list
        """
        element_maker = lxml.builder.ElementMaker()

        xml_string = lxml.etree.tostring(
            element_maker.Body(
                self.__create_odm_xml_task_list(element_maker, stop_action, action_format),
                self.__create_odm_xml_node_list(element_maker),
                self.__create_odm_xml_transition_list(
                    element_maker, attribute_formatter, operator_formatter,
                    join_operator_formatter, numerical_value_formatter,
                    categorical_value_formatter),
            ), pretty_print=True
        ).decode('utf-8')
        return xml_string

    def __create_odm_xml_task_list(self, element_maker, stop_action: str, action_format: str):
        task_list = element_maker.TaskList()
        task_list.append(element_maker.StartTask(Identifier='start_task'))
        task_list.append(element_maker.StopTask(element_maker.Actions(
            lxml.etree.CDATA(stop_action + ' ; '), Language='bal'
        ), Identifier='stop_task'))
        for node in sorted(self.__event_flow_graph.nodes(), key=lambda n: n.node_id):
            task_list.append(element_maker.ActionTask(element_maker.Actions(
                lxml.etree.CDATA(action_format % node.event + ' ; '), Language='bal'
            ), Identifier=f'{node.node_id}|{node.event}'))
        return task_list

    def __create_odm_xml_node_list(self, element_maker):
        node_list = element_maker.NodeList()
        node_list.append(element_maker.TaskNode(Identifier='node_0', Task='start_task'))
        node_list.append(element_maker.TaskNode(Identifier='node_1', Task='stop_task'))
        for node in sorted(self.__event_flow_graph.nodes(), key=lambda n: n.node_id):
            node_list.append(element_maker.TaskNode(
                Identifier=f'node_{node.node_id}',
                Task=f'{node.node_id}|{node.event}'))

        for node, router in self.__node_router_table.items():
            #-2, because we do not need branching nodes if there is only one
            #condition or less. the last element is a default rule
            for i in range(len(router.get_rule().get_rule()) - 2):
                node_list.append(element_maker.BranchNode(Identifier=f'branch_{node.node_id}_{i}'))

        return node_list

    def __create_odm_xml_transition_list(
            self, element_maker, attribute_formatter: Callable[[str], str],
            operator_formatter: Callable[[str], str],
            join_operator_formatter: Callable[[str], str],
            numerical_value_formatter: Callable[[float], str],
            categorical_value_formatter: Callable[[Any], str]):
        transition_list = element_maker.TransitionList()
        id_generator = iter(range(sys.maxsize))
        for edge in sorted(self.__event_flow_graph.edges(),
                           key=lambda e: (e.from_node.node_id, e.to_node.node_id)):
            if edge.from_node not in self.__node_router_table:
                transition_list.append(element_maker.Transition(
                    Identifier=f'transition_{next(id_generator)}',
                    Source=f'node_{edge.from_node.node_id}',
                    Target=f'node_{edge.to_node.node_id}'))
        for node, router in sorted(
                self.__node_router_table.items(), key=lambda x: x[0].node_id):
            branch_id_generator = iter(range(sys.maxsize))
            current_node_id = f'node_{node.node_id}'
            rule_list = router.get_rule().get_rule().get_list()
            while rule_list:
                if len(rule_list) == 1:
                    transition = element_maker.Transition(
                        Identifier=f'transition_{next(id_generator)}',
                        Source=current_node_id,
                        Target=f'node_{rule_list[0].get_class_label()}')
                else:
                    transition = element_maker.Transition(
                        Identifier=f'transition_{next(id_generator)}',
                        Source=current_node_id,
                        Target=f'node_{rule_list[0].get_if_branch()[0].get_class_label()}')
                    transition.append(element_maker.Conditions(
                        lxml.etree.CDATA(rule_list[0].get_condition().to_bal(
                            attribute_formatter=attribute_formatter,
                            operator_formatter=operator_formatter,
                            join_operator_formatter=join_operator_formatter,
                            numerical_value_formatter=numerical_value_formatter,
                            categorical_value_formatter=categorical_value_formatter
                        )),
                        Language='bal'
                    ))
                transition_list.append(transition)
                if len(rule_list) > 2:
                    branch_node_id = f'branch_{node.node_id}_{next(branch_id_generator)}'
                    transition_list.append(element_maker.Transition(
                        Identifier=f'transition_{next(id_generator)}',
                        Source=current_node_id,
                        Target=branch_node_id))
                    current_node_id = branch_node_id

                rule_list = rule_list[1:]

        return transition_list