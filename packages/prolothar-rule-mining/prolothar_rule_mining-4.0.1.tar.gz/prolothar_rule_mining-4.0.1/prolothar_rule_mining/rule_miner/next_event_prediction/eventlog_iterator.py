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
from typing import Tuple, Generator

from prolothar_common.models.eventlog import EventLog, Trace, Event
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph

__EMPTY_EVENT_FLOW_GRAPH = EventFlowGraph()

def eventlog_iterator(eventlog: EventLog) -> Generator[Tuple[Trace, str], None, None]:
    """
    enables iteration on an eventlog that outputs tuples
    (prefix of a trace: Trace, next_activity_name: str)
    """
    source_event = Event(__EMPTY_EVENT_FLOW_GRAPH.source.event)
    for trace in eventlog:
        for i in range(len(trace)):
            yield (
                Trace(
                    '%s-%d' % (str(trace.get_id()), i),
                    [source_event] + trace.events[:i],
                    trace.attributes
                ),
                trace.events[i].activity_name
            )
        yield (
            Trace(
                '%s-%d' % (str(trace.get_id()), len(trace)),
                [source_event] + trace.events,
                trace.attributes
            ),
            __EMPTY_EVENT_FLOW_GRAPH.sink.event
        )

