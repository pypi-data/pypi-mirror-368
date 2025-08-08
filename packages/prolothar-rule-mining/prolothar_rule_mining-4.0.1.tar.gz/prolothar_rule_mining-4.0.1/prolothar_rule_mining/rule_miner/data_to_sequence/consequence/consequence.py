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
module of the rule discovery algorithm ConSequence
"""

from typing import Callable
import itertools

from prolothar_common.parallel.abstract.computation_engine import ComputationEngine
from prolothar_common.parallel.single_thread.single_thread import SingleThreadComputationEngine

from prolothar_common.models.dataset import Dataset

from prolothar_rule_mining.models.event_flow_graph.cover import compute_cover
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph import Node
from prolothar_rule_mining.models.event_flow_graph.router.learning import RuleClassifierRouterLearner
from prolothar_rule_mining.models.event_flow_graph.alignment.petrinet import PetrinetAligner

from prolothar_rule_mining.rule_miner.classification.rce import ReliableRuleMiner

from prolothar_rule_mining.rule_miner.data_to_sequence.rules import Rule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.event_flow_graph_rule import EventFlowGraphRule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.event_flow_graph_rule import Router

from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.event_flow_graph_miner import EventFlowGraphMiner
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.event_flow_graph_miner import SequenceBottomUpEventFlowGraphMiner

def learn_router_at_decision_node(parameters, node: Node) -> Router:
    if parameters.get('logger', None) is not None:
        parameters['logger'](f'learn decision rule at {node}')
    return node, parameters['router_learner'](
        node, parameters['event_flow_graph'], parameters['dataset'])

class ConSequence():
    """
    splits inference of a Data2Sequence model into two subproblems:
    1. derive an EventFlowGraph from the sequence database
    2. learn the rules for routing sequences given their attributes through this graph
    """

    def __init__(self, logger: Callable[[str], None] = print,
                 event_flow_graph_miner: EventFlowGraphMiner = None,
                 router_learner: Callable[[Node, EventFlowGraph, Dataset], Router] = None,
                 computation_engine: ComputationEngine = None):
        """
        constructor with multiple options how to run the algorithm

        Parameters
        ----------
        logger : Callable[[str], None], optional
            this is used for debug information, by default print. if you want
            to turn off logging, set this to "lambda x: None"
        event_flow_graph_miner : EventFlowGraphMiner, optional
            by default None
        router_learner : Callable[[Node, EventFlowGraph, Dataset], Router], optional
            by default None
        computation_engine : ComputationEngine, optional
            can be used to parallelize computations, by default None (means single thread execution)
        """
        if event_flow_graph_miner is not None:
            self.__event_flow_graph_miner = event_flow_graph_miner
        else:
            self.__event_flow_graph_miner = SequenceBottomUpEventFlowGraphMiner(
                logger=logger, patience=10,
                alignment_finder_factory_model_extension=PetrinetAligner)
        if router_learner is not None:
            self.__router_learner = router_learner
        else:
            self.__router_learner = RuleClassifierRouterLearner(ReliableRuleMiner(logger=logger))
        self.__logger = logger
        if computation_engine is None:
            self.__computation_engine = SingleThreadComputationEngine()
        else:
            self.__computation_engine = computation_engine

    def mine_rules(self, dataset: Dataset) -> Rule:
        event_flow_graph = self.__event_flow_graph_miner.mine_event_flow_graph(dataset)
        return self.infer_rules_from_event_flow_graph(event_flow_graph, dataset)

    def infer_rules_from_event_flow_graph(
            self, event_flow_graph: EventFlowGraph, dataset: Dataset):
        compute_cover(dataset, event_flow_graph, assign_instances_to_edges=True,
                      alignment_finder=PetrinetAligner(event_flow_graph))

        #it might be that the event flow graph was mined with a greedy alignment
        #which differs from the optimal alignment. hence, it can happen, that
        #the optimal alignment does not use some edges/nodes. So, let us remove
        #them

        event_flow_graph.remove_edges_without_instances()

        node_router_table = {}
        decision_node_list = self.__computation_engine.create_partitionable_list([
            node for node in itertools.chain(event_flow_graph.nodes(),
                                             [event_flow_graph.source])
            if len(node.children) > 1
        ])

        parameters = {
            'router_learner': self.__router_learner,
            'event_flow_graph': event_flow_graph,
            'dataset': dataset
        }
        if isinstance(self.__computation_engine, SingleThreadComputationEngine):
            parameters['logger'] = self.__logger
        for node, router in decision_node_list.map(
                parameters, learn_router_at_decision_node, keep_order=False):
            node_router_table[node] = router

        rule = EventFlowGraphRule(event_flow_graph, node_router_table)

        #remove dead branches not reachable due to mined rules
        #=> this can happen if the learned classifiers considered routes as noise
        for edge in event_flow_graph.edges():
            edge.attributes['nr_of_instances'] = 0
        for instance in dataset:
            rule.execute(instance, add_nr_of_instances_to_edges=True)

        for edge in list(event_flow_graph.edges()):
            if edge.attributes['nr_of_instances'] == 0 \
            and len(edge.from_node.children) > 1 \
            and edge.to_node not in node_router_table[edge.from_node].get_set_of_output_nodes():
                event_flow_graph.remove_edge(edge)
        event_flow_graph.remove_illegal_source_nodes()

        return rule

    def __repr__(self) -> str:
        return 'ConSequence(%r,%r)' % (self.__event_flow_graph_miner, self.__router_learner)
