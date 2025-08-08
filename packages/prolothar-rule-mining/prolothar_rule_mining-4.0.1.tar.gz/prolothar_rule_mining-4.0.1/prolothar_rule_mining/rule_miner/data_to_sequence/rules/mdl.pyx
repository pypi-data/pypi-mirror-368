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
from typing import Dict, Set, List
from collections import Counter

from math import log2
from lru import LRU

import prolothar_common.mdl_utils as mdl_utils
from prolothar_common.levenshtein import levenshtein_with_backtrace
from prolothar_common.levenshtein import EditOperationType
from prolothar_common.models.dataset import Dataset
from prolothar_common.models.dataset.instance import Instance
from prolothar_rule_mining.rule_miner.data_to_sequence.rules import Rule

InstanceToEditsCounter = Dict[Instance, Dict[EditOperationType, int]]

class EditDistanceCache:
    """
    LRU Cache for min edit distance computations on sequences. can be used as
    a parameter for the compute_mdl function
    """
    def __init__(self, max_cache_size: int):
        self.__lru: LRU = LRU(max_cache_size)
        self.__hits = 0
        self.__misses = 0

    def get_distance(self, sequence_a: List[str], sequence_b: tuple[str]):
        cache_key = (tuple(sequence_a), sequence_b)
        try:
            distance = self.__lru[cache_key]
            self.__hits += 1
            return distance
        except KeyError:
            self.__misses += 1
            distance = _compute_edit_operation_counter(sequence_a, sequence_b)
            self.__lru[cache_key] = distance
            return distance

class MdlComputationDetails:
    """
    stores details of the computation including partial results. can be used
    to compute gain estimates for modifications of the model
    """
    def __init__(self):
        self.mdl_of_model: float = None
        self.mdl_of_data: float = None
        self.instance_to_mdl: Dict[Instance, float] = {}
        self.instance_to_edits_counter: InstanceToEditsCounter = {}
        self.instance_to_missing_symbols_counter: Dict[Instance, Dict[str, int]] = {}
        self.instance_to_generated_sequence_length: Dict[Instance, Dict[str, int]] = {}
        self.nr_of_attributes: int = None
        self.set_of_symbols: Set[str] = None

    def get_total_mdl(self) -> float:
        """returns mdl_of_model + mdl_of_data"""
        return self.mdl_of_model + self.mdl_of_data

    def copy(self) -> 'MdlComputationDetails':
        """returns a deep copy"""
        copy = MdlComputationDetails()
        copy.mdl_of_model = self.mdl_of_model
        copy.mdl_of_data = self.mdl_of_data
        copy.instance_to_mdl = dict(self.instance_to_mdl)

        copy.instance_to_edits_counter = {}
        for instance, dictionary in self.instance_to_edits_counter.items():
            copy.instance_to_edits_counter[instance] = dict(dictionary)

        copy.instance_to_missing_symbols_counter = {}
        for instance, dictionary in self.instance_to_missing_symbols_counter.items():
            copy.instance_to_missing_symbols_counter[instance] = Counter(dictionary)

        copy.instance_to_generated_sequence_length = dict(
            self.instance_to_generated_sequence_length)

        copy.mdl_of_model = self.mdl_of_model
        copy.mdl_of_model = self.mdl_of_model

        copy.nr_of_attributes = self.nr_of_attributes
        copy.set_of_symbols = set(self.set_of_symbols)
        return copy

def compute_mdl(dataset: Dataset, rule: Rule, verbose: bool = False,
                computation_details: MdlComputationDetails = None,
                edit_distance_cache: EditDistanceCache = None) -> float:
    """
    computes the minimum description length of the dataset and the rule as
    a model of the dataset. L(dataset,rule) = L(rule) + L(dataset|rule)

    Parameters
    ----------
    dataset : Dataset
        the dataset containing instances with feature attributes and
        target sequences.
    rule : Rule
        a rule to generate sequences from the feature attributes of an
        instance. a low L(dataset|rule) means that the rule is able to generate
        sequences close to the target sequences in the dataset, i.e. fits the
        dataset better. a low L(rule) means the model is simple.
    verbose : bool, optional
        if True, partial results are printed. The default is False.
    computation_details : MdlComputationDetails, optional
        used to store partial results which can be used to compute estimates
        when modifying the rule. The default is None.
    edit_distance_cache : EditDistanceCache, optional
        can be used to cache results for the edit distance computations between
        sequences, which is used to compute the data encoding length.

    Returns
    -------
    float
        the encoded length of the rule plus the dataset given the rule.
        lower means better.
    """
    mdl_of_model = compute_mdl_of_model(rule, dataset,verbose=verbose)
    mdl_of_data = compute_mdl_of_data(
        dataset, rule, computation_details = computation_details,
        edit_distance_cache=edit_distance_cache)

    if computation_details is not None:
        computation_details.mdl_of_model = mdl_of_model
        computation_details.mdl_of_data = mdl_of_data
        computation_details.nr_of_attributes = dataset.get_nr_of_attributes()
        computation_details.set_of_symbols = dataset.get_set_of_sequence_symbols()

    if verbose or mdl_of_model < 0 or mdl_of_data < 0:
        print('L(M): %f' % mdl_of_model)
        print('L(D|M): %f' % mdl_of_data)

    return mdl_of_model + mdl_of_data

def compute_mdl_of_model(rule: Rule, dataset: Dataset,
                         verbose: bool = False) -> float:
    """model (rule) part of the MDL"""
    return rule.compute_mdl(dataset.get_set_of_sequence_symbols(),
                            dataset.get_nr_of_attributes())

def compute_mdl_of_data(
        dataset: Dataset, rule: Rule,
        computation_details: MdlComputationDetails = None,
        edit_distance_cache: EditDistanceCache = None) -> float:
    """
    computes L(D|M) = L(dataset|rule)

    Parameters
    ----------
    dataset : Dataset
        the dataset containing instances with feature attributes and
        target sequences
    rule : Rule
        a rule to generate sequences from the feature attributes of an
        instance. a low L(D|M) means that the rule is able to generate
        sequences close to the target sequences in the dataset
    computation_details : MdlComputationDetails, optional
        used to store partial results which can be used to compute estimates
        when modifying the rule. The default is None.
    edit_distance_cache: EditDistanceCache, optional
        can be set to cache the necessary edit distance computations

    Returns
    -------
    float
        L(D|M). a low L(D|M) means that the rule is able to generate
        sequences close to the target sequences in the dataset

    """
    mdl_data = 0
    for instance in dataset:
        mdl_data += compute_mdl_of_instance(
                instance, rule, dataset.get_set_of_sequence_symbols(),
                computation_details = computation_details,
                edit_distance_cache = edit_distance_cache)
    return mdl_data

def compute_mdl_of_instance(
        instance: Instance, rule: Rule, symbol_set: Set[str],
        computation_details: MdlComputationDetails = None,
        edit_distance_cache: EditDistanceCache = None) -> float:
    """
    computes the ecnoded length of a single instance

    Parameters
    ----------
    instance : Instance
        the instance for which to compute the encoded length.
    rule : Rule
        used to generate a sequence from the feature attributes of the
        given instance
    symbol_set : Set[str]
        the set of symbols/events of the whole dataset that can be used to
        build up the target sequences of the instances
    computation_details : MdlComputationDetails, optional
        used to store partial results which can be used to compute estimates
        when modifying the rule. The default is None.
    edit_distance_cache: EditDistanceCache, optional
        can be set to cache the necessary edit distance computations

    Returns
    -------
    float
        the encoded length of the given instance. the lower the better is
        the model able to generate the target sequence of the given instance
    """
    generated_sequence = rule.execute(instance)
    if computation_details is not None:
        computation_details.instance_to_generated_sequence_length[
            instance] = len(generated_sequence)
    if edit_distance_cache is not None:
        counter = edit_distance_cache.get_distance(
            generated_sequence, instance.get_target_sequence())
    else:
        counter = _compute_edit_operation_counter(
            generated_sequence, instance.get_target_sequence())

    mdl_of_instance = compute_mdl_of_instance_using_edits_counter(
        counter, symbol_set, len(generated_sequence))

    if computation_details is not None:
        computation_details.instance_to_edits_counter[instance] = counter
        computation_details.instance_to_mdl[instance] = mdl_of_instance
        missing_symbols_counter = Counter(instance.get_target_sequence())
        for generated_symbol in generated_sequence:
            missing_symbols_counter[generated_symbol] -= 1
        computation_details.instance_to_missing_symbols_counter[
            instance] = missing_symbols_counter

    return mdl_of_instance

def _compute_edit_operation_counter(
        generated_sequence : list[str],
        target_sequence: tuple[str]) -> Dict[EditOperationType, int]:
    """
    computes how many edit operations for each edit operations type are necessary
    to transform the generated_sequence to the target_sequence

    Parameters
    ----------
    generated_sequence : List[str]
    target_sequence : List[str]

    Returns
    -------
    Dict[EditOperationType, int]
        the required number of operations per type to transform generated_sequence
        to target_sequence
    """
    _,edits = levenshtein_with_backtrace(generated_sequence, target_sequence,
                                         substitution_cost = 2)
    counter = {
        EditOperationType.DELETE: 0,
        EditOperationType.INSERT: 0,
        EditOperationType.SUBSTITUTE: 0
    }
    for edit in edits:
        counter[edit.operation_type] += 1
    substitute_count = counter[EditOperationType.SUBSTITUTE]
    if substitute_count > 0:
        counter[EditOperationType.DELETE] += substitute_count
        counter[EditOperationType.INSERT] += substitute_count
        counter[EditOperationType.SUBSTITUTE] = 0
    return counter

def compute_mdl_of_instance_using_edits_counter(
        edits_counter: Dict[EditOperationType, int], symbol_set: Set[str],
        length_of_generated_sequence: int) -> float:
    """
    computes the mdl of a single instance given the number of edit operations
    per EditOperationType

    Parameters
    ----------
    edits_counter : Dict[EditOperationType, int]
        assigns the number of edit operations per type necessary to transform
        the generated sequence into the actual garget sequence of the instance
    instance : Instance
        the instance for which to compute the encoded length.
    symbol_set : Set[str]
        the set of symbols/events of the whole dataset that can be used to
        build up the target sequences of the instances

    Returns
    -------
    float
        the encoded length of the given instance. the lower the better is
        the model able to generate the target sequence of the given instance
    """
    if edits_counter[EditOperationType.SUBSTITUTE] > 0:
        raise ValueError('substitute operations are not allowed')
    nr_of_deletes = edits_counter[EditOperationType.DELETE]
    nr_of_inserts = edits_counter[EditOperationType.INSERT]

    #nr (can be 0) of deletes
    mdl = mdl_utils.L_N(nr_of_deletes + 1)
    if nr_of_deletes > 0:
        #positions (one position cannot be chosen twice)
        mdl += mdl_utils.log2binom(length_of_generated_sequence, nr_of_deletes)

    length_of_generated_sequence -= nr_of_deletes

    #nr (can be 0) of inserts
    mdl += mdl_utils.L_N(nr_of_inserts + 1)
    if nr_of_inserts > 0:
        #positions (one position can be chosen multiple times)
        # mdl += mdl_utils.log2binom(
        #         length_of_generated_sequence + nr_of_inserts,
        #         nr_of_inserts)
        mdl += mdl_utils.sum_log_i_from_1_to_n(
            length_of_generated_sequence + nr_of_inserts
        )
        if length_of_generated_sequence > 0:
            mdl -= mdl_utils.sum_log_i_from_1_to_n(length_of_generated_sequence)
        #symbols
        mdl += nr_of_inserts * log2(len(symbol_set))

    return mdl

