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
from typing import Tuple, Union, Dict

from random import Random

from collections import defaultdict
import itertools
import networkx as nx

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.models.dataset.instance import TargetSequenceInstance
from prolothar_rule_mining.models.dataset_generator.dataset_generator import DatasetGenerator
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph import Node
from prolothar_rule_mining.models.event_flow_graph.cover import compute_cover
from prolothar_rule_mining.models.event_flow_graph.alignment.petrinet import PetrinetAligner
from prolothar_rule_mining.models.conditions import Condition, OrCondition
from prolothar_rule_mining.rule_miner.data_to_sequence.rules import Rule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.event_flow_graph_rule import EventFlowGraphRule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules.event_flow_graph_rule import RuledRouter
from prolothar_rule_mining.rule_miner.data_to_sequence.rules import ListOfRules
from prolothar_rule_mining.rule_miner.data_to_sequence.rules import AppendRule
from prolothar_rule_mining.rule_miner.data_to_sequence.rules import IfThenElseRule
from prolothar_rule_mining.rule_miner.classification.rules import FirstFiringRuleModel
from prolothar_rule_mining.rule_miner.classification.rules import ListOfRules as ListOfClassificationRules
from prolothar_rule_mining.rule_miner.classification.rules import ReturnClassRule
from prolothar_rule_mining.rule_miner.classification.rules import IfThenElseRule as IfThenElseClassificationRule

class TargetSequenceDatasetGenerator(DatasetGenerator):
    """
    generates an artificial dataset and rules for target sequence generation
    under some parameters
    """

    def __init__(self, nr_of_categorical_features: int = 5,
                 nr_of_categories: int = 3,
                 nr_of_numerical_features: int = 5,
                 nr_of_instances: int = 100,
                 nr_of_sequence_symbols: int = 10,
                 max_condition_depth: int = 0,
                 model: str = 'list',
                 max_rule_depth: int = 1,
                 min_rule_length: Union[Dict[int,int], int] = 1,
                 max_rule_length: Union[Dict[int,int], int] = 10,
                 max_nr_of_nodes_in_model: int = 25,
                 edge_probability: float = 0.1,
                 random: Random = None):
        """
        configures the dataset generator

        Parameters
        ----------
        nr_of_categorical_features : int, optional
            number of categorical features in the generated dataset, by default 5
        nr_of_categories : int, optional
            number of categories (unique values) for categorical features, by default 3
        nr_of_numerical_features : int, optional
            number of numerical (continuous) features to generate, by default 5
        nr_of_instances : int, optional
            number of instances in the generated dataset, by default 100
        nr_of_sequence_symbols : int, optional
            size of the event alphabet that is used for model generation, by default 10
        max_condition_depth : int, optional
            the maximal number of terms in a condition is (max_condition_depth+1),
            by default 0
        model : str, optional
            type of the rule model that should be generated:
            - list: a ListOfRules is generated
            - eventflowgraph: an EventFlowGraphRule is generated
            - eventflowgraph2: first a ListOfRules is generated, which is then
                converted to an eventflow graph. finally, the split rules are
                regenerated. generates thinner but longer models than "eventflowgraph"
            by default 'list'
        max_rule_depth : int, optional
            maximal depth of generated rules. only applies if model == 'list',
            by default 1
        min_rule_length : Union[Dict[int,int], int], optional
            only applies if model == 'list', by default 1
        max_rule_length : Union[Dict[int,int], int], optional
            only applies if model == 'list', by default 10
        max_nr_of_nodes_in_model : int, optional
            only applies if model == 'eventflowgraph', by default 25
        edge_probability : float, optional
            only applies if model == 'eventflowgraph', a value between 0 and 1.
            the higher the value, the more edges will be in the model.
            by default 0.1
        random : Random, optional
            random generator. can be set to fix randomness, by default None
        """
        super().__init__(
            nr_of_categorical_features = nr_of_categorical_features,
            nr_of_categories = nr_of_categories,
            nr_of_numerical_features = nr_of_numerical_features,
            nr_of_instances = nr_of_instances,
            max_condition_depth = max_condition_depth,
            random = random)
        if isinstance(min_rule_length, int):
            self.__min_rule_length = defaultdict(lambda: min_rule_length)
        else:
            self.__min_rule_length = min_rule_length
            if any (v for v in min_rule_length.values() if v < 1):
                raise ValueError('min_rule_length must not be < 1, but was %r' %
                                min_rule_length)
        if isinstance(max_rule_length, int):
            self.__max_rule_length = defaultdict(lambda: max_rule_length)
        else:
            self.__max_rule_length = max_rule_length
        for depth in set(self.__min_rule_length.keys()).union(self.__max_rule_length.keys()):
            if (self.__max_rule_length[depth] < self.__min_rule_length[depth]):
                raise ValueError(
                    'max_rule_length must not be < min_rule_length, but %d < %d for depth %d' %
                    self.__min_rule_length[depth], self.__max_rule_length[depth], depth)
        if isinstance(min_rule_length, int) and isinstance(max_rule_length, int) \
        and max_rule_length < min_rule_length:
            raise ValueError(
                'max_rule_length must not be < min_rule_length, but %d < %d' %
                min_rule_length, max_rule_length)
        self.__max_rule_depth = max_rule_depth
        if nr_of_sequence_symbols < 1:
            raise ValueError('nr_of_sequence_symbols must not be < 1, but was %d' %
                             nr_of_sequence_symbols)
        self.__nr_of_sequence_symbols = nr_of_sequence_symbols
        self.__max_nr_of_nodes_in_model = max_nr_of_nodes_in_model
        self.__edge_probability = edge_probability
        self.__model = model

    def generate(self) -> Tuple[TargetSequenceDataset, Rule]:
        """returns an artificially generated dataset and rules for target
        sequence generation"""
        dataset = self.generate_features_only_dataset()
        if self.__model == 'list':
            rule = self.__generate_list_of_rules(dataset)
        elif self.__model == 'eventflowgraph':
            rule = self.__generate_event_flow_graph_rule(dataset)
        elif self.__model == 'eventflowgraph2':
            rule = self.__generate_event_flow_graph_rule_from_graph(
                self.__generate_list_of_rules(dataset).to_eventflow_graph(), dataset)
        else:
            raise NotImplementedError('unknown model type: %s' % self.__model)
        dataset = self.apply_rule_to_dataset(dataset, rule)
        if self.__model in ['eventflowgraph', 'eventflowgraph2']:
            self.__prune_dead_branches(rule, dataset)
        return dataset, rule

    def generate_with_completely_random_target_sequences(self) -> TargetSequenceDataset:
        """
        returns an artificially generated dataset and with random target
        sequences s.t. there is no functional dependency between features
        and target sequences
        """
        dataset = self.generate_features_only_dataset()
        dataset = self.__add_random_target_sequences(dataset)
        return dataset

    def generate_with_shuffled_sequences(self) -> TargetSequenceDataset:
        """
        returns an artificially generated dataset and with shuffled
        sequences s.t. there is no functional dependency between features
        and target sequences
        """
        dataset,_ = self.generate()
        shuffled_dataset = TargetSequenceDataset(
            dataset.get_categorical_attribute_names(),
            dataset.get_numerical_attribute_names())
        shuffled_sequences = [instance.get_target_sequence() for instance in dataset]
        self._random.shuffle(shuffled_sequences)
        for i,instance in enumerate(dataset):
            shuffled_dataset.add_instance(TargetSequenceInstance(
                instance.get_id(), instance.get_features_dict(),
                shuffled_sequences[i]
            ))
        return shuffled_dataset

    def __add_random_target_sequences(self, dataset: TargetSequenceDataset) -> TargetSequenceDataset:
        dataset_with_sequences = TargetSequenceDataset(
            dataset.get_categorical_attribute_names(),
            dataset.get_numerical_attribute_names())
        for instance in dataset:
            sequence = []
            for _ in range(self._random.randint(self.__min_rule_length[0],
                                                 self.__max_rule_length[0])):
                sequence.append(str(self._random.choice(
                        range(self.__nr_of_sequence_symbols))))
            dataset_with_sequences.add_instance(TargetSequenceInstance(
                instance.get_id(), instance.get_features_dict(), sequence))
        return dataset_with_sequences

    def __generate_event_flow_graph_rule(self, dataset: TargetSequenceDataset) -> Rule:
        random_graph = nx.fast_gnp_random_graph(
            self.__max_nr_of_nodes_in_model, self.__edge_probability)
        random_dag = nx.DiGraph([
            (u,v) for u,v in random_graph.edges() if u < v
        ])
        event_flow_graph = EventFlowGraph()
        node_id_node_dict = {}
        for node_id in random_dag.nodes():
            node = event_flow_graph.add_node(str(
                self._random.randrange(0, self.__nr_of_sequence_symbols)))
            node_id_node_dict[node_id] = node
        for u,v in random_dag.edges():
            event_flow_graph.add_edge(
                node_id_node_dict[u], node_id_node_dict[v])
        return self.__generate_event_flow_graph_rule_from_graph(
            event_flow_graph, dataset)

    def __generate_event_flow_graph_rule_from_graph(
            self, event_flow_graph: EventFlowGraph,
            dataset: TargetSequenceDataset) -> EventFlowGraphRule:
        event_flow_graph.merge_redundant_nodes()

        node_router_table = {}
        for node in event_flow_graph.nodes():
            if len(node.parents) == 0:
                event_flow_graph.add_edge(event_flow_graph.source, node)
            if len(node.children) == 0:
                event_flow_graph.add_edge(node, event_flow_graph.sink)
        for node in itertools.chain(event_flow_graph.nodes(), [event_flow_graph.source]):
            node_router_table[node] = self.__generate_router(node, dataset)

        return EventFlowGraphRule(event_flow_graph, node_router_table)

    def __generate_router(self, node: Node, dataset: TargetSequenceDataset) -> RuledRouter:
        children = list(node.children)
        self._random.shuffle(children)
        rule = ListOfClassificationRules()
        for child in children[:-1]:
            while True:
                condition = self._generate_condition(dataset)
                if not self.__is_subset_of_existing_condition(rule, condition):
                    break
            rule.append_rule(IfThenElseClassificationRule(
                condition,
                if_branch=ListOfClassificationRules([
                    ReturnClassRule(str(child.node_id))
                ])
            ))

        rule.append_rule(ReturnClassRule(str(children[-1].node_id)))
        rule = FirstFiringRuleModel(rule)
        return RuledRouter({child.node_id: child for child in children}, rule)

    def __is_subset_of_existing_condition(
        self, rule_list: ListOfClassificationRules, condition: Condition) -> bool:
        """
        c1 is a subset of c2 if (c1 or c2) can be minimized to c2.
        """
        for rule in rule_list:
            combined_condition = OrCondition([condition, rule.get_condition()])
            minimized_condition = combined_condition.compress()
            if minimized_condition == rule.get_condition():
                return True
        return False

    def __prune_dead_branches(
            self, rule: EventFlowGraphRule,
            dataset: TargetSequenceDataset):
        set_of_nodes_before_pruning = set(rule.get_event_flow_graph().nodes())

        compute_cover(
            dataset, rule.get_event_flow_graph(), assign_instances_to_edges=True,
            alignment_finder=PetrinetAligner(rule.get_event_flow_graph()))
        rule.get_event_flow_graph().remove_edges_without_instances()

        for pruned_node in set_of_nodes_before_pruning.difference(
                rule.get_event_flow_graph().nodes()):
            if pruned_node in rule.get_node_router_table():
                rule.get_node_router_table().pop(pruned_node)
            for router in rule.get_node_router_table().values():
                router.get_rule().remove_rules_containing_symbol(str(pruned_node.node_id))
                #ensure that at least one rule fires
                if len(router.get_rule().get_rule()) > 0 \
                and isinstance(router.get_rule().get_rule()[-1], IfThenElseClassificationRule):
                    router.get_rule().get_rule()[-1] = router.get_rule().get_rule()[-1].get_if_branch()[0]

        for node in itertools.chain(
                rule.get_event_flow_graph().nodes(),
                [rule.get_event_flow_graph().source]):
            if len(node.children) == 1 and node in rule.get_node_router_table():
                rule.get_node_router_table().pop(node)

    def __generate_list_of_rules(
            self, dataset: TargetSequenceDataset, depth: int = 0) -> Rule:
        rule_length = self._random.randint(
                self.__min_rule_length[depth], self.__max_rule_length[depth])
        rule = ListOfRules()
        rule.set_subdataset(dataset)
        for _ in range(rule_length):
            #dataset.get_nr_of_attributes() <= 0 ensures that conditions are only
            #tried to be generated if there is at least one attribute to build
            #conditions
            if depth >= self.__max_rule_depth \
            or self._random.choice([True, dataset.get_nr_of_attributes() <= 0]):
                rule.append_rule(AppendRule(str(self._random.choice(
                        range(self.__nr_of_sequence_symbols)))))
            else:
                condition = self._generate_condition(dataset)
                if_dataset,else_dataset = condition.divide_dataset(dataset)
                rule.append_rule(IfThenElseRule(
                    condition,
                    if_branch=self.__generate_list_of_rules(
                            if_dataset, depth=depth+1),
                    else_branch=self.__generate_list_of_rules(
                            else_dataset, depth=depth+1)))
        return rule

    def apply_rule_to_dataset(
            self, dataset: TargetSequenceDataset, rule: Rule) -> TargetSequenceDataset:
        dataset_with_sequences = TargetSequenceDataset(
                [attribute.get_name() for attribute in dataset.get_attributes()
                 if attribute.is_categorical()],
                [attribute.get_name() for attribute in dataset.get_attributes()
                 if attribute.is_numerical()])
        for instance in dataset:
            sequence = rule.execute(instance)
            dataset_with_sequences.add_instance(TargetSequenceInstance(
                    instance.get_id(), instance.get_features_dict(), sequence))
        return dataset_with_sequences