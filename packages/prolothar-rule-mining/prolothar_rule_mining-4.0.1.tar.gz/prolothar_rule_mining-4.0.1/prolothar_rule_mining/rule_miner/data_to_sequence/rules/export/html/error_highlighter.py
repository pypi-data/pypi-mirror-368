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
from collections import defaultdict, Counter
from typing import Dict

from bs4 import BeautifulSoup

from prolothar_common.levenshtein import levenshtein_with_backtrace
from prolothar_common.levenshtein import EditOperationType

from prolothar_common.models.dataset import Dataset
from prolothar_rule_mining.rule_miner.data_to_sequence.rules import ListOfRules

RULE_STYLE = (
    '<style>'
        '.AppendRule {border-bottom: dotted 1px;}'
        '.AppendRule .MissingSymbols {float: right;}'
        '.AppendRule .MissingSymbol {margin-left: 0.5em;}'
        '.ListOfRules > .MissingSymbols > .MissingSymbol {margin-right: 0.5em;}'
        '.MissingSymbol {display: inline-block;}'
        '.MissingSymbol .symbol {'
            'margin-right: 0.2778em;'
            'font-style: italic;'
            'color: gray;}'
        '.MissingSymbol .count::before {content: "("}'
        '.MissingSymbol .count::after {content: ")"}'
        '.if {display: inline-block; margin-right: 0.2778em}'
        '.IfThenElseRule > .Condition {display: inline-block;}'
        '.ifbranch, .elsebranch {margin-left: 1em;}'
        '.Condition {display: inline-block;}'
        '.Operator, .JoinOperatorCondition {margin-left: 0.2778em; margin-right: 0.2778em;}'
    '</style>'
)

class ErrorHighlighter():

    def highlight(self, model: ListOfRules, dataset: Dataset) -> str:
        """
        exports the given model to a error highlighted html representation

        Parameters
        ----------
        model : ListOfRules
            will be exported to html code. parts that make mistakes on the given
            dataset will be highlighted
        dataset : Dataset
            will be checked against the model to highlight errors

        Returns
        -------
        str
            error highlighted html representation of the given model
        """
        html = BeautifulSoup(model.to_html(), 'html.parser')

        missing_symbols_counter = defaultdict(lambda: defaultdict(Counter))
        wrong_symbol_counter = defaultdict(Counter)
        for instance in dataset:
            predicted_sequence, model_backtrace = model.execute_with_backtrace(instance)
            _, edit_operations_list = levenshtein_with_backtrace(
                predicted_sequence, instance.get_target_sequence())

            nr_of_added_symbols = Counter()

            for edit_operation in edit_operations_list:
                if edit_operation.i < len(model_backtrace):
                    submodel = model_backtrace[edit_operation.i][0]
                    model_index = model_backtrace[edit_operation.i][2]
                else:
                    submodel = model
                    model_index = len(model)

                if edit_operation.operation_type == EditOperationType.INSERT:
                    model_index += nr_of_added_symbols[id(submodel)]
                    missing_symbols_counter[id(submodel)][model_index][
                        instance.get_target_sequence()[edit_operation.j]] += 1
                    nr_of_added_symbols[id(submodel)] += 1
                elif edit_operation.operation_type == EditOperationType.SUBSTITUTE:
                    wrong_symbol_counter[id(submodel[model_index])][
                        instance.get_target_sequence()[edit_operation.j]
                    ] += 1
                else:
                    wrong_symbol_counter[id(submodel[model_index])]['""'] += 1

        for rule_id, index_missing_symbols_counter in missing_symbols_counter.items():
            for index, missing_symbols in index_missing_symbols_counter.items():
                self.__add_missing_symbols_highlighting(
                    html, rule_id, index, missing_symbols, len(dataset), False)

        for rule_id, symbol_counter in wrong_symbol_counter.items():
            self.__add_missing_symbols_highlighting(
                html, rule_id, 0, symbol_counter, len(dataset), True)

        return RULE_STYLE + str(html)

    def __add_missing_symbols_highlighting(
            self, html: BeautifulSoup, rule_id: int, index: int,
            missing_symbols_counter: Dict[str, int], nr_of_instances: int,
            is_replacement: bool):
        rule_div = html.find(id=rule_id)
        missing_symbols_div = html.new_tag('div')
        missing_symbols_div['class'] = 'MissingSymbols'
        background_style = 'background: rgba(255,0,0,%.1f)' % (
            sum(missing_symbols_counter.values()) / nr_of_instances
        )
        if is_replacement:
            rule_div['style'] = background_style
        else:
            missing_symbols_div['style'] = background_style
        for symbol, count in missing_symbols_counter.items():
            missing_symbol_div = html.new_tag('div')
            missing_symbol_div['class'] = 'MissingSymbol'

            symbol_span = html.new_tag('span')
            symbol_span.append(symbol)
            symbol_span['class'] = 'symbol'
            missing_symbol_div.append(symbol_span)

            count_span = html.new_tag('span')
            count_span.append(str(count))
            count_span['class'] = 'count'
            missing_symbol_div.append(count_span)

            missing_symbols_div.append(missing_symbol_div)
        rule_div.insert(index, missing_symbols_div)
