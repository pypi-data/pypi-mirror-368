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
this module contains the cover model and the necessary methods to compute a cover.
a cover describes how an EventFlowGraph is used to describe the target sequences
of a given dataset
"""

from prolothar_rule_mining.models.event_flow_graph.cover.cover import Cover
from prolothar_rule_mining.models.event_flow_graph.cover.cover import CoverStep
from prolothar_rule_mining.models.event_flow_graph.cover.cover_computer import compute_cover
from prolothar_rule_mining.models.event_flow_graph.cover.cover_computer import CoverComputer
from prolothar_rule_mining.models.event_flow_graph.cover.model_code_counter import ModelCodeCounter
