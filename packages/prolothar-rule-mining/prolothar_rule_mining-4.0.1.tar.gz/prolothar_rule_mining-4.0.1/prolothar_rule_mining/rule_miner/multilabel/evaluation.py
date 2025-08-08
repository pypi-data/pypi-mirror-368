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

from statistics import harmonic_mean

from prolothar_common.models.dataset import MultiLabelDataset

from prolothar_rule_mining.rule_miner.multilabel.rules.rule import Rule

class Evaluation():
    """
    data object that stores evaluation metrics
    """
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    false_negatives: int = 0
    micro_precision: float
    micro_recall: float
    micro_f1: float

def evaluate(rule: Rule, dataset: MultiLabelDataset) -> Evaluation:
    """
    evaluates the performance of the given rule on the given dataset

    Parameters
    ----------
    rule : Rule
        rule for which the prediction performance will be measured
    dataset : MultiLabelDataset
        dataset on which the prediction performance will be measured

    Returns
    -------
    Evaluation
        a data object that stores the evaluation metrics
    """
    evaluation = Evaluation()

    for instance in dataset:
        predicted_labels = rule.predict(instance)
        actual_labels = instance.get_labels()
        evaluation.true_positives += len(predicted_labels.intersection(actual_labels))
        evaluation.false_positives += len(predicted_labels.difference(actual_labels))
        evaluation.false_negatives += len(actual_labels.difference(predicted_labels))
    try:
        evaluation.micro_precision = evaluation.true_positives / (
            evaluation.true_positives + evaluation.false_positives)
    except ZeroDivisionError:
        evaluation.micro_precision = 1
    if evaluation.true_positives + evaluation.false_negatives == 0:
        evaluation.micro_recall = 1
    else:
        evaluation.micro_recall = evaluation.true_positives / (
            evaluation.true_positives + evaluation.false_negatives)
    evaluation.micro_f1 = harmonic_mean([evaluation.micro_precision, evaluation.micro_recall])

    return evaluation