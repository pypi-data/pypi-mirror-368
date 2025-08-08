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
this module provides classes that give an cached interface to operations on an
EventFlowGraph that are normally uncached, e.g. shortest path computation.
"""

from typing import List, Union, Dict

from prolothar_rule_mining.models.event_flow_graph.graph import EventFlowGraph
from prolothar_rule_mining.models.event_flow_graph.node import Node

class CachedShortestPathToEventFinder:
    """
    caches the computation of shortest path to events given a start node
    """

    def __init__(self, graph: EventFlowGraph):
        self.__shortest_path_to_event_cache: Dict[Node, Union[None, List[Node]]] = {}
        self.__graph = graph

    def __call__(self, node: Node, event: str) -> Union[None, List[Node]]:
        try:
            return self.__shortest_path_to_event_cache[(node,event)]
        except KeyError:
            path = self.__graph.find_shortest_path_to_event(node, event)
            self.__shortest_path_to_event_cache[(node, event)] = path
            return path

class CachedShortestPathsToEventFinder:
    """
    caches the computation of shortest paths to events given a start node
    """

    def __init__(self, graph: EventFlowGraph):
        self.__shortest_paths_to_event_cache: Dict[Node, Union[None, List[List[Node]]]] = {}
        self.__graph = graph

    def __call__(self, node: Node, event: str) -> Union[None, List[List[Node]]]:
        try:
            return self.__shortest_paths_to_event_cache[(node,event)]
        except KeyError:
            paths = self.__graph.find_shortest_paths_to_event(node, event)
            self.__shortest_paths_to_event_cache[(node, event)] = paths
            return paths
