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
implements future path prediction with data aware transition systems (dats)
based on the paper
"Time and Activity Sequence Prediction of Business Process Instances"
by Polato et al.
https://andrea.burattin.net/public-files/publications/2018-computing.pdf
"""

from typing import Callable, Tuple, Dict, List, Hashable
from math import log2
from collections import defaultdict
import itertools
from more_itertools import ilen, pairwise
import networkx as nx

from prolothar_common.parallel.abstract.computation_engine import ComputationEngine
from prolothar_common.parallel.single_thread.single_thread import SingleThreadComputationEngine

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.models.dataset import ClassificationDataset
from prolothar_common.models.dataset.instance import Instance
from prolothar_common.models.dataset.instance import ClassificationInstance

from prolothar_common.models.labeled_transition_system import LabeledTransitionSystem
from prolothar_common.models.labeled_transition_system.labeled_transition_system import State, Transition
from prolothar_common.models.labeled_transition_system.state_representation import set_abstraction

from prolothar_rule_mining.rule_miner.classification.naive_bayes import MixedNaiveBayesClassifier
from prolothar_rule_mining.rule_miner.classification.rules.sklearn import TrainedSklearnClassifier

def _learn_classifier(parameters, state_and_dataset: Tuple[State, ClassificationDataset]):
    state, dataset = state_and_dataset
    return state, parameters['classifier_type'](**parameters['classifier_parameters']).mine_rules(dataset)

class DatsRule:

    def __init__(
            self, transition_system: LabeledTransitionSystem,
            state_classifier_dict: Dict[State, TrainedSklearnClassifier]):
        self.__transition_system = transition_system
        self.__state_classifier_dict = state_classifier_dict

    def execute(self, instance: Instance) -> List[str]:
        """
        generates an event sequence based on the attributes of the given instance
        """
        transition_probabilities = self.__compute_transition_probabilities(instance)
        state_graph = self.__build_state_graph_with_costs(transition_probabilities)
        shortest_path = nx.dijkstra_path(
            state_graph,
            str(next(iter(self.__transition_system.get_start_states()))),
            '_END_')[:-1]
        return [state_graph[s1][s2]['event'] for s1,s2 in pairwise(shortest_path)]

    def __build_state_graph_with_costs(self, transition_probabilities) -> nx.DiGraph:
        edges = [
            (str(transition[0]), str(transition[2]))
            for transition in transition_probabilities
        ]
        for end_state in self.__transition_system.get_end_states():
            edges.append((str(end_state), '_END_'))
        graph = nx.DiGraph(edges)
        nx.set_edge_attributes(graph, {
            (str(transition[0]), str(transition[2])): {
                'weight': -log2(max(probability, 0.0001)),
                'event': transition[1]
            } for transition, probability in itertools.chain(
                transition_probabilities.items(),
                (((end_state, None, '_END_'), 1) for end_state in self.__transition_system.get_end_states()))

        })
        return graph

    def get_nr_of_nodes(self) -> int:
        return self.__transition_system.get_nr_of_states()

    def __compute_transition_probabilities(self, instance: Instance) -> Dict[Transition, float]:
        transition_probabilities = {}
        for state in self.__transition_system.get_states():
            if state in self.__state_classifier_dict:
                try:
                    predicted_probability = self.__state_classifier_dict[state].predict_proba(instance)
                except KeyError:
                    #the instance has a categorical value that has never been seen at this state
                    predicted_probability = defaultdict(lambda: 1 / ilen(
                        self.__transition_system.yield_outgoing_transitions(state)))
                for transition in self.__transition_system.yield_outgoing_transitions(state):
                    transition_probabilities[transition] = predicted_probability[str(transition[1])]
            else:
                for transition in self.__transition_system.yield_outgoing_transitions(state):
                    transition_probabilities[transition] = 1
        return transition_probabilities

    def get_transition_system(self) -> LabeledTransitionSystem:
        return self.__transition_system

class Dats:
    """
    mines a Data-Aware-Transition-System to predict a sequence given an
    attribute vector
    """

    def __init__(
            self, state_representation_function: Callable[[List[Hashable]], State] = set_abstraction,
            computation_engine: ComputationEngine = SingleThreadComputationEngine(),
            classifier_type = MixedNaiveBayesClassifier,
            classifier_parameters: Dict = None,
            min_relative_sequence_frequency: float = 0.0):
        self.__state_representation_function = state_representation_function
        self.__computation_engine = computation_engine
        self.__classifier_type = classifier_type
        if classifier_parameters is not None:
            self.__classifier_parameters = classifier_parameters
        else:
            self.__classifier_parameters = {}
        self.__min_relative_sequence_frequency = min_relative_sequence_frequency

    def mine_rules(self, dataset: TargetSequenceDataset) -> DatsRule:
        dataset = self.__filter_dataset(dataset)

        transition_system = self.__build_transition_system(dataset)

        state_dataset_dict = self.__create_state_dataset_dict(
            dataset, transition_system)

        processable_list = self.__computation_engine.create_partitionable_list(
            [(state, dataset) for state, dataset in state_dataset_dict.items()])

        state_classifier_dict = {}
        for state, classifier in processable_list.map(
                {
                    'classifier_type': self.__classifier_type,
                    'classifier_parameters': self.__classifier_parameters,
                }, _learn_classifier, keep_order=False):
            state_classifier_dict[state] = classifier

        return DatsRule(transition_system, state_classifier_dict)

    def __filter_dataset(self, dataset: TargetSequenceDataset) -> TargetSequenceDataset:
        if self.__min_relative_sequence_frequency == 0.0:
            return dataset
        sequence_frequency_dict = defaultdict(int)
        for instance in dataset:
            sequence_frequency_dict[instance.get_target_sequence()] += 1
        min_absolute_frequency = max(
            sequence_frequency_dict.values()) * self.__min_relative_sequence_frequency
        filtered_dataset = TargetSequenceDataset(
            dataset.get_categorical_attribute_names(),
            dataset.get_numerical_attribute_names())
        for instance in dataset:
            if sequence_frequency_dict[instance.get_target_sequence()] >= min_absolute_frequency:
                filtered_dataset.add_instance(instance)
        return filtered_dataset

    def __build_transition_system(self, dataset: TargetSequenceDataset) -> LabeledTransitionSystem:
        transition_system = LabeledTransitionSystem(
            state_representation_function=self.__state_representation_function
        )
        for instance in dataset:
            transition_system.add_sequence(instance.get_target_sequence())
        return transition_system

    def __create_state_dataset_dict(
            self, dataset: TargetSequenceDataset,
            transition_system: LabeledTransitionSystem):
        state_dataset_dict = {
            state: ClassificationDataset(
                dataset.get_categorical_attribute_names(),
                dataset.get_numerical_attribute_names()
            )
            for state in transition_system.get_states()
            if ilen(transition_system.yield_outgoing_transitions(state)) > 1
        }

        if len(transition_system.get_start_states()) != 1:
            raise NotImplementedError(
                f'there is not exactly one start state: {transition_system.get_start_states()}')

        id_counter = itertools.count()
        for instance in dataset:
            current_state = next(iter(transition_system.get_start_states()))
            for event in instance.get_target_sequence():
                next_state = transition_system.get_next_state(current_state, event)
                if current_state in state_dataset_dict:
                    state_dataset_dict[current_state].add_instance(ClassificationInstance(
                        next(id_counter),
                        instance.get_features_dict(),
                        event
                    ))
                current_state = next_state

        return state_dataset_dict

