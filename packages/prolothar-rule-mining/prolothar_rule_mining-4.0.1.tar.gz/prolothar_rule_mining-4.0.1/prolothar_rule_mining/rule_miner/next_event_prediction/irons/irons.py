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
from typing import Iterable, Union, List, Set

from collections import defaultdict, Counter
from strsimpy.normalized_levenshtein import NormalizedLevenshtein

from prolothar_common.models.eventlog import EventLog, Trace
from prolothar_common.models.dataset import TargetSequenceDataset, ClassificationDataset
from prolothar_common.models.dataset.instance import TargetSequenceInstance, ClassificationInstance
from prolothar_common.models.dataset.transformer.remove_attrs_with_one_value import RemoveAttributesWithOneUniqueValue

from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph, Node
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence.event_flow_graph_miner import EventFlowGraphMiner

from prolothar_rule_mining.rule_miner.next_event_prediction.eventlog_iterator import eventlog_iterator

class Irons:
    """
    mine "interpretable rules on next step"
    """

    def __init__(self, event_flow_graph_miner: EventFlowGraphMiner,
                 categorical_attribute_names: Iterable[str],
                 numerical_attribute_names: Iterable[str],
                 classifier):
        self.__event_flow_graph_miner = event_flow_graph_miner
        self.__dataset_per_node = {}
        self.__categorical_attribute_names = set(categorical_attribute_names)
        self.__numerical_attribute_names = set(numerical_attribute_names)
        self.__classifier = classifier
        self.__classifier_per_node = {}
        self.__prefixes_per_node = defaultdict(set)
        self.__eventflow_graph: Union[EventFlowGraph, None] = None
        self.__alphabet: Union[Set[str], None] = None
        self.__dataset_per_prefix = {}
        self.__classifier_per_prefix = {}

    def train(self, eventlog: EventLog):
        self.__alphabet = eventlog.compute_activity_set()
        dataset = TargetSequenceDataset([], [])
        for trace in eventlog:
            dataset.add_instance(TargetSequenceInstance(
                trace.get_id(), {}, trace.to_activity_list()
            ))
        self.__eventflow_graph = self.__event_flow_graph_miner.mine_event_flow_graph(dataset)

        for prefix_trace, next_activity in eventlog_iterator(eventlog):
            training_node_list = self.__find_nodes_by_prefix(prefix_trace)
            if training_node_list:
                for training_node in training_node_list:
                    self.__add_instance_to_node(prefix_trace, next_activity, training_node)
            else:
                self.__add_instance_to_prefix(prefix_trace, next_activity)

        self.__train_classifier()

    def __find_nodes_by_prefix(self, prefix_trace: Trace) -> Set[Node]:
        node_list = set()
        self.__recursively_find_nodes_by_prefix(
            self.__eventflow_graph.source, prefix_trace.to_activity_list()[1:], 0, node_list)
        return node_list

    def __recursively_find_nodes_by_prefix(
            self, current_node: Node, prefix: List[str], event_pointer: int,
            node_list: Set[Node]):
        if event_pointer == len(prefix):
            node_list.add(current_node)
        else:
            for child in current_node.children:
                if child.event == prefix[event_pointer]:
                    self.__recursively_find_nodes_by_prefix(
                        child, prefix, event_pointer + 1, node_list)

    def predict(self, prefix_trace: Trace) -> str:
        node_list = self.__find_nodes_by_prefix(prefix_trace)
        if node_list:
            votes = Counter()
            for node in node_list:
                votes[self.__predict_from_node(node, prefix_trace)] += 1
            return max(votes.items(), key=lambda x: x[1])[0]
        try:
            prefix = tuple(prefix_trace.to_activity_list())
            return self.__classifier_per_prefix[prefix].predict(
                self.__trace_to_instance(prefix_trace, ''))
        except KeyError:
            node = self.__select_node_for_prediction(prefix_trace)
            return self.__predict_from_node(node, prefix_trace)

    def __predict_from_node(self, node: Node, prefix_trace: Trace) -> str:
        if node not in self.__classifier_per_node:
            if len(node.children) == 1:
                return next(iter(node.children))
            else:
                self.__eventflow_graph.plot(show=False, with_node_ids=True, filepath='temp1')
                raise NotImplementedError(node, node.children)
        return self.__classifier_per_node[node].predict(
            self.__trace_to_instance(prefix_trace, ''))

    def __select_node_for_prediction(self, prefix_trace) -> Node:
        candidate_nodes = [
            node for node in self.__eventflow_graph.nodes()
            if node.event == prefix_trace.events[-1].activity_name
        ]
        if len(candidate_nodes) == 1:
            return candidate_nodes[0]
        elif len(candidate_nodes) == 0:
            if len(prefix_trace) == 1:
                return self.__eventflow_graph.source
            return self.__select_node_for_prediction(Trace(
                prefix_trace.get_id(),
                prefix_trace.events[:-1],
                attributes = prefix_trace.attributes
            ))
        else:
            return self.__select_node_with_most_similar_instances(
                candidate_nodes, prefix_trace)

    def __select_node_with_most_similar_instances(
            self, candidate_nodes: List[Node], prefix_trace: Trace) -> Node:
        best_similarity = -1
        best_node = None
        prefix_trace = prefix_trace.to_activity_list()
        for node in candidate_nodes:
            node_similarity = 0
            for sequence in self.__prefixes_per_node[node]:
                node_similarity = max(
                    node_similarity,
                    NormalizedLevenshtein().similarity(prefix_trace, sequence))
                if node_similarity == 1.0:
                    break
            if node_similarity > best_similarity:
                best_similarity = node_similarity
                best_node = node
        return best_node

    def __add_instance_to_node(self, prefix_trace: Trace, next_activity: str, node: Node):
        instance = self.__trace_to_instance(prefix_trace, next_activity)
        if node not in self.__dataset_per_node:
            self.__dataset_per_node[node] = ClassificationDataset(
                self.__categorical_attribute_names.intersection(
                    instance.get_feature_names()).union(self.__alphabet),
                self.__numerical_attribute_names.intersection(instance.get_feature_names()),
            )
        self.__dataset_per_node[node].add_instance(instance)
        self.__prefixes_per_node[node].add(tuple(prefix_trace.to_activity_list()))

    def __add_instance_to_prefix(self, prefix_trace: Trace, next_activity: str):
        instance = self.__trace_to_instance(prefix_trace, next_activity)
        prefix = tuple(prefix_trace.to_activity_list())
        if prefix not in self.__dataset_per_prefix:
            self.__dataset_per_prefix[prefix] = ClassificationDataset(
                self.__categorical_attribute_names.intersection(
                    instance.get_feature_names()).union(self.__alphabet),
                self.__numerical_attribute_names.intersection(instance.get_feature_names()),
            )
        self.__dataset_per_prefix[prefix].add_instance(instance)

    def __trace_to_instance(
            self, trace: Trace, next_activity: str) -> ClassificationInstance:
        attributes = {}
        for attribute_name, attribute_value in trace.attributes.items():
            if attribute_name in self.__categorical_attribute_names \
            or attribute_name in self.__numerical_attribute_names:
                attributes[attribute_name] = attribute_value
        for event in trace.events:
            for attribute_name, attribute_value in event.attributes.items():
                if attribute_name in self.__categorical_attribute_names \
                or attribute_name in self.__numerical_attribute_names:
                    attributes[attribute_name] = attribute_value
        for event in self.__alphabet:
            attributes[event] = 'absent'
        #"1:" because we do not want "epsilon" (start of trace signal)
        for event in trace.events[1:]:
            attributes[event.activity_name] = 'present'
        return ClassificationInstance(
            trace.get_id(),
            attributes,
            next_activity
        )

    def __train_classifier(self):
        for node, classification_dataset in self.__dataset_per_node.items():
            RemoveAttributesWithOneUniqueValue().inplace_transform(classification_dataset)
            self.__classifier_per_node[node] = self.__classifier.mine_rules(classification_dataset)

        for prefix, classification_dataset in self.__dataset_per_prefix.items():
            RemoveAttributesWithOneUniqueValue().inplace_transform(classification_dataset)
            self.__classifier_per_prefix[prefix] = self.__classifier.mine_rules(classification_dataset)
