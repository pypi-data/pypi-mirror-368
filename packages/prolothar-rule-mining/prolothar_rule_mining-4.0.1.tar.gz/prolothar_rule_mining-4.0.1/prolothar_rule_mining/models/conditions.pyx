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
from typing import List, Tuple, Set, Callable, Any
from collections import defaultdict

import numpy as np
from math import log2

import html

from prolothar_common.func_tools import identity
import prolothar_common.mdl_utils as mdl_utils
from prolothar_common.models.dataset import Dataset
from prolothar_common.models.dataset.instance cimport Instance

#IN,EQUALS
cdef float CODE_LENGTH_FOR_CATEGORICAL_OPERATOR_CHOICE = log2(2)
#<,>
cdef float CODE_LENGTH_FOR_NUMERICAL_OPERATOR_CHOICE = log2(2)

#NOT,AND,OR,IN,EQUALS,<,>
cdef float CODE_LENGTH_FOR_CONDITION_TYPE_CHOICE = log2(7)

cdef class Condition:

    cpdef bint check_instance(self, Instance instance):
        """returns True iff the given instance fullfils this condition"""
        raise NotImplementedError()

    cpdef float compute_mdl(self, int nr_of_attributes):
        """computes the minimum-description-length of this condition"""
        return CODE_LENGTH_FOR_CONDITION_TYPE_CHOICE

    def count_nr_of_terms(self) -> int:
        """
        returns the number of terms (atomic conditions).
        "If a > 2 and b <= 3 then append(x)" returns 2
        """
        raise NotImplementedError()

    def compress(self) -> Condition:
        """
        returns a compressed version with removed redundancy of this condition.
        Example:
        ("num_feature_7" <= 0.655 and "num_feature_11" > 0.082) and "num_feature_11" > 0.184
        is condensed to
        ("num_feature_7" <= 0.655 and "num_feature_11" > 0.184).

        if there is no compression possible, then the condition itself is returned
        """
        raise NotImplementedError()

    def get_set_of_used_attributes(self) -> Set[str]:
        """
        returns the set of attributes that are used in this condition
        """
        raise NotImplementedError()

    def divide_dataset(self, dataset: Dataset) -> Tuple[Dataset, Dataset]:
        """splits a dataset into matching and non-matching instances"""
        if_instances = []
        else_instances = []
        for instance in dataset:
            if self.check_instance(instance):
                if_instances.append(instance)
            else:
                else_instances.append(instance)
        return (dataset.get_subdataset(if_instances),
                dataset.get_subdataset(else_instances))

    def to_html(self) -> str:
        """
        returns a human readable html string representation of this condition
        """
        raise NotImplementedError()

    def to_bal(self, attribute_formatter: Callable[[str], str] = identity,
               operator_formatter: Callable[[str], str] = identity,
               join_operator_formatter: Callable[[str], str] = identity,
               numerical_value_formatter: Callable[[float], str] = str,
               categorical_value_formatter: Callable[[Any], str] = str) -> str:
        """
        export to the BAL language of IBM ODM
        """
        raise NotImplementedError()

    def __repr__(self):
        return str(self)

cdef class AttributeCondition(Condition):
    """consists of <Attribute> <Operator> <Value(s)>"""
    def __init__(self, attribute, operator_symbol: str, value):
        if value is None:
            raise ValueError('value must not be None')
        self.attribute = attribute
        self.operator_symbol = operator_symbol
        self.value = value

    def __eq__(self, other) -> bool:
        try:
            return (self.value == other.value and
                    self.operator_symbol == other.operator_symbol and
                    self.attribute.get_name() == other.attribute.get_name())
        except AttributeError as e:
            return False

    def __hash__(self) -> int:
        return hash((self.attribute.get_name(), self.operator_symbol,
                     self.value))

    cpdef bint check_instance(self, instance: Instance):
        return self.check_value(instance[self.attribute.get_name()])

    def count_nr_of_terms(self) -> int:
        return 1

    def get_set_of_used_attributes(self) -> Set[str]:
        return set([self.attribute.get_name()])

    def get_attribute(self):
        return self.attribute

    cdef bint check_value(self, tested_value):
        """returns True iff the condition is fullfilled by the given value"""
        raise NotImplementedError()

    cpdef float compute_mdl(self, int nr_of_attributes):
        cdef float mdl = Condition.compute_mdl(self, nr_of_attributes)
        mdl += log2(nr_of_attributes)
        if self.attribute.is_categorical():
            mdl += CODE_LENGTH_FOR_CATEGORICAL_OPERATOR_CHOICE
        elif self.attribute.is_numerical():
            mdl += CODE_LENGTH_FOR_NUMERICAL_OPERATOR_CHOICE
        else:
            raise NotImplementedError(type(self.attribute))
        if isinstance(self.value, list) or isinstance(self.value, set):
            #how many values? domain size is upper bound
            mdl += log2(self.attribute.get_nr_of_unique_values())
            mdl += mdl_utils.log2binom(
                    self.attribute.get_nr_of_unique_values(),
                    len(self.value))
        else:
            mdl += log2(self.attribute.get_nr_of_unique_values())
        return mdl

    def compress(self) -> Condition:
        return self

    def __str__(self):
        return '"%s" %s %s' % (
            self.attribute.get_name(),
            self.operator_symbol,
            self._get_formatted_value()
        )

    def _get_formatted_value(self) -> str:
        if self.attribute.is_categorical():
            return '"' + str(self.value) + '"'
        else:
            return np.format_float_positional(self.value, 3, trim='-').rstrip('.')

    def to_html(self) -> str:
        return ('<div class="Condition AttributeCondition">'
                    '<span class="Attribute">%s</span>'
                    '<span class="Operator">%s</span>'
                    '<span class="Value">%s</span>'
                '</div>') % (
                    self.attribute.get_name(),
                    html.escape(self.operator_symbol),
                    self._get_formatted_value()
                )

    def to_bal(self, attribute_formatter: Callable[[str], str] = identity,
               operator_formatter: Callable[[str], str] = identity,
               join_operator_formatter: Callable[[str], str] = identity,
               numerical_value_formatter: Callable[[float], str] = str,
               categorical_value_formatter: Callable[[Any], str] = str) -> str:
        if self.attribute.is_categorical():
            value_formatter = categorical_value_formatter
        else:
            value_formatter = numerical_value_formatter
        return '%s %s %s' % (
            attribute_formatter(self.attribute.get_name()),
            operator_formatter(self.operator_symbol),
            value_formatter(self.value)
        )

    def get_value(self):
        return self.value

cdef class EqualsCondition(AttributeCondition):
    """tests equality of an attribute value"""
    def __init__(self, attribute, value):
        super().__init__(attribute, '=', value)
        if not attribute.is_categorical():
            raise TypeError(type(attribute))

    cpdef bint check_value(self, tested_value):
        return tested_value == self.get_value()

cdef class InCondition(AttributeCondition):
    """tests set membership of an attribute value"""
    def __init__(self, attribute, value):
        super().__init__(attribute, 'in', value)
        if not attribute.is_categorical():
            raise TypeError(type(attribute))

    cpdef bint check_value(self, tested_value):
        return tested_value in self.get_value()

cdef class InRangeCondition(AttributeCondition):
    """tests set membership of an attribute value"""
    def __init__(
            self, attribute, lower_bound, upper_bound,
            lower_bound_inclusive: bool = False, upper_bound_inclusive: bool = True):
        super().__init__(attribute, 'in', (lower_bound, upper_bound))
        if not attribute.is_numerical():
            raise TypeError(type(attribute))
        self.lower_bound_inclusive = lower_bound_inclusive
        self.upper_bound_inclusive = upper_bound_inclusive

    cpdef bint check_value(self, tested_value):
        return (
            (
                tested_value > self.value[0] or (
                    self.lower_bound_inclusive and tested_value == self.value[0])
            )
            and
            (
                tested_value < self.value[1] or (
                    self.upper_bound_inclusive and tested_value == self.value[1])
            )
        )

    def _get_formatted_value(self) -> str:
        lower_bound_bracket = '[' if self.lower_bound_inclusive else '('
        upper_bound_bracket = ']' if self.upper_bound_inclusive else ')'
        lower_value = np.format_float_positional(self.value[0], 3, trim='-').rstrip('.')
        upper_value = np.format_float_positional(self.value[1], 3, trim='-').rstrip('.')
        return f'{lower_bound_bracket}{lower_value}, {upper_value}{upper_bound_bracket}'

cdef class GreaterOrEqualCondition(AttributeCondition):
    """tests >= of an attribute value"""
    def __init__(self, attribute, value):
        super().__init__(attribute, '>=', value)
        if not attribute.is_numerical():
            raise TypeError(type(attribute))

    cpdef bint check_value(self, tested_value):
        return tested_value >= self.get_value()

cdef class GreaterThanCondition(AttributeCondition):
    """tests > of an attribute value"""
    def __init__(self, attribute, value):
        super().__init__(attribute, '>', value)
        if not attribute.is_numerical():
            raise TypeError(type(attribute))

    cpdef bint check_value(self, tested_value):
        return tested_value > self.get_value()

cdef class LessOrEqualCondition(AttributeCondition):
    """tests <= of an attribute value"""
    def __init__(self, attribute, value):
        super().__init__(attribute, '<=', value)
        if not attribute.is_numerical():
            raise TypeError(type(attribute))

    cpdef bint check_value(self, tested_value):
        return tested_value <= self.get_value()

cdef class LessThanCondition(AttributeCondition):
    """tests < of an attribute value"""
    def __init__(self, attribute, value):
        super().__init__(attribute, '<', value)
        if not attribute.is_numerical():
            raise TypeError(type(attribute))

    cpdef bint check_value(self, tested_value):
        return tested_value < self.get_value()

cdef class NotCondition(Condition):
    cdef public Condition condition

    """negates another condition"""
    def __init__(self, Condition condition):
        self.condition = condition

    def __eq__(self, other) -> bool:
        try:
            return (isinstance(other, NotCondition) and
                    self.condition == other.condition)
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return hash((False, self.condition))

    cpdef Condition get_condition(self):
        return self.condition

    cpdef bint check_instance(self, instance: Instance):
        return not self.condition.check_instance(instance)

    def count_nr_of_terms(self) -> int:
        return self.condition.count_nr_of_terms()

    def get_set_of_used_attributes(self) -> Set[str]:
        return self.condition.get_set_of_used_attributes()

    def compress(self) -> Condition:
        if isinstance(self.get_condition, NotCondition) :
            return self.get_condition.get_condition().compress()
        return NotCondition(self.get_condition.compress())

    cpdef float compute_mdl(self, int nr_of_attributes):
        cdef float mdl = Condition.compute_mdl(self, nr_of_attributes)
        mdl += self.condition.compute_mdl(nr_of_attributes)
        return mdl

    def __str__(self):
        return 'not %s' % self.condition

    def to_html(self) -> str:
        return ('<div cdef class="Condition NotCondition">%s</div>') % (
                    self.condition.to_html()
                )

cdef class JoinOperatorCondition(Condition):
    """a condition that joins multiple conditions"""
    cdef public list conditions
    cdef public str join_operator

    def __init__(self, conditions: List[Condition], join_operator: str):
        if len(conditions) < 2:
            raise ValueError('at least two conditions must be joined')
        self.conditions = conditions
        self.join_operator = join_operator

    def __eq__(self, other) -> bool:
        try:
            if self.join_operator != other.join_operator \
            or len(self.conditions) != len(other.conditions):
                return False
            for a,b in zip(self.conditions, other.conditions):
                if a != b:
                    return False
            return True
        except AttributeError as e:
            return False

    def __hash__(self) -> int:
        value = hash(self.join_operator)
        for condition in self.conditions:
            value = value ^ hash(condition)
        return value

    def get_conditions(self) -> List[Condition]:
        return self.conditions

    cpdef int count_nr_of_terms(self):
        cdef int nr_of_terms = 0
        for condition in self.conditions:
            nr_of_terms += condition.count_nr_of_terms()
        return nr_of_terms

    def get_set_of_used_attributes(self) -> Set[str]:
        used_attributes = set()
        for condition in self.conditions:
            used_attributes.update(condition.get_set_of_used_attributes())
        return used_attributes

    cpdef float compute_mdl(self, int nr_of_attributes):
        cdef float mdl = Condition.compute_mdl(self, nr_of_attributes)
        mdl += mdl_utils.L_N(len(self.conditions) - 1)
        for condition in self.conditions:
            mdl += condition.compute_mdl(nr_of_attributes)
        return mdl

    def __repr__(self):
        return '(' + (' ' + self.join_operator + ' ').join(
            str(c) for c in self.get_conditions()) + ')'

    def to_html(self) -> str:
        join_operator = '<span cdef class="JoinOperator">%s</span>' % html.escape(
            self.join_operator)
        return '<div cdef class="Condition JoinOperatorCondition">%s</div>' % (
                    join_operator.join(c.to_html() for c in self.conditions))

    def _group_conditions_by_type_and_attributes(self):
        grouped_conditions = defaultdict(list)
        for condition in self.get_conditions():
            if type(condition) is type(self):
                for subcondition in condition.get_conditions():
                    compressed_condition = subcondition.compress()
                    grouped_conditions[
                        (type(compressed_condition),
                        frozenset(compressed_condition.get_set_of_used_attributes()))
                    ].append(compressed_condition)
            else:
                compressed_condition = condition.compress()
                grouped_conditions[
                    (type(compressed_condition),
                     frozenset(compressed_condition.get_set_of_used_attributes()))
                ].append(compressed_condition)
        return grouped_conditions

    def to_bal(self, attribute_formatter: Callable[[str], str] = identity,
               operator_formatter: Callable[[str], str] = identity,
               join_operator_formatter: Callable[[str], str] = identity,
               numerical_value_formatter: Callable[[float], str] = str,
               categorical_value_formatter: Callable[[Any], str] = str) -> str:
        return '(' + f' {join_operator_formatter(self.join_operator)} '.join(
            condition.to_bal(
                attribute_formatter=attribute_formatter,
                operator_formatter=operator_formatter,
                join_operator_formatter=join_operator_formatter,
                numerical_value_formatter=numerical_value_formatter,
                categorical_value_formatter=categorical_value_formatter
            ) for condition in self.conditions
        ) + ')'

def split_singleton_conditions(conditions: List[Condition]) -> Tuple[
        List[Condition], List[JoinOperatorCondition]]:
    """
    splits the given list of conditions into singletons
    (i.e. AttributeCondition, NotCondition) and composites (i.e. JoinedAttributeCondition)

    Returns
    -------
    Tuple[ List[Condition], List[JoinOperatorCondition]]
        a list of singleton conditions and a list of composite conditions
    """
    singleton_conditions = []
    composite_conditions = []
    for condition in conditions:
        if isinstance(condition, JoinOperatorCondition):
            composite_conditions.append(condition)
        else:
            singleton_conditions.append(condition)
    return singleton_conditions, composite_conditions

cdef class AndCondition(JoinOperatorCondition):
    """AND operator for conditions"""
    def __init__(self, conditions: List[Condition]):
        super().__init__(conditions, 'and')

    cpdef bint check_instance(self, Instance instance):
        for condition in self.get_conditions():
            if not condition.check_instance(instance):
                return False
        return True

    def compress(self) -> Condition:
        grouped_conditions = self._group_conditions_by_type_and_attributes()

        compressed_conditions = []
        for group_key, conditions in grouped_conditions.items():
            condition_type, set_of_attributes = group_key
            if len(set_of_attributes) > 1 or len(conditions) == 1:
                compressed_conditions.extend(conditions)
            elif condition_type == GreaterThanCondition:
                compressed_conditions.append(max(conditions, key=AttributeCondition.get_value))
            elif condition_type == LessThanCondition or condition_type == LessOrEqualCondition:
                compressed_conditions.append(min(conditions, key=AttributeCondition.get_value))
            elif condition_type == EqualsCondition:
                compressed_conditions.extend(set(conditions))
            else:
                raise NotImplementedError((condition_type, set_of_attributes, conditions))

        compressed_conditions = self.__minimize_conditions_using_identity_rules(compressed_conditions)

        if len(compressed_conditions) > 1:
            return AndCondition(compressed_conditions)
        else:
            return compressed_conditions[0]

    def __minimize_conditions_using_identity_rules(self, compressed_conditions: List[Condition]):
        singleton_conditions, composite_conditions = split_singleton_conditions(
            compressed_conditions)
        for singleton in singleton_conditions:
            compressed_conditions.append(singleton)
            for composite in list(compressed_conditions):
                if isinstance(composite, OrCondition) \
                and singleton in composite.get_conditions():
                    composite_conditions.remove(composite)
        return singleton_conditions + composite_conditions

cdef class OrCondition(JoinOperatorCondition):
    """OR operator for conditions"""
    def __init__(self, conditions: List[Condition]):
        super().__init__(conditions, 'or')

    cpdef bint check_instance(self, instance: Instance):
        for condition in self.get_conditions():
            if condition.check_instance(instance):
                return True
        return False

    def compress(self) -> Condition:
        grouped_conditions = self._group_conditions_by_type_and_attributes()

        compressed_conditions = []
        for group_key, conditions in grouped_conditions.items():
            condition_type, set_of_attributes = group_key
            if len(set_of_attributes) > 1 or len(conditions) == 1:
                compressed_conditions.extend(conditions)
            elif condition_type == GreaterThanCondition:
                compressed_conditions.append(min(conditions, key=AttributeCondition.get_value))
            elif condition_type == LessThanCondition or condition_type == LessOrEqualCondition:
                compressed_conditions.append(max(conditions, key=AttributeCondition.get_value))
            elif condition_type == EqualsCondition:
                compressed_conditions.extend(set(conditions))
            else:
                raise NotImplementedError((condition_type, set_of_attributes, conditions))

        compressed_conditions = self.__minimize_conditions_using_identity_rules(compressed_conditions)

        if len(compressed_conditions) > 1:
            return OrCondition(compressed_conditions)
        else:
            return compressed_conditions[0]

    def __minimize_conditions_using_identity_rules(self, compressed_conditions: List[Condition]):
        singleton_conditions, composite_conditions = split_singleton_conditions(
            compressed_conditions)
        for singleton in singleton_conditions:
            compressed_conditions.append(singleton)
            for composite in list(compressed_conditions):
                if isinstance(composite, AndCondition) \
                and singleton in composite.get_conditions():
                    composite_conditions.remove(composite)
        return singleton_conditions + composite_conditions



