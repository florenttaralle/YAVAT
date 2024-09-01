from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List
import itertools as it
from src.models.event import EventModel
from src.models.annotation import AnnotationModel, QColor

class TimelineModel(AnnotationModel):
    event_added         = pyqtSignal(EventModel)
    "SIGNAL: event_added(event: EventModel)"
    event_removed       = pyqtSignal(EventModel)
    "SIGNAL: event_removed(event: EventModel)"
    
    next_id_generator = it.count()
    
    def __init__(self, duration: int, name: str|None=None, color: QColor|str=None, visible: bool=True, selected: bool=False, 
                 events: List[EventModel]=None, parent: QObject|None=None):
        if name is None:
            name = f"Timeline {next(self.next_id_generator)}"
        AnnotationModel.__init__(self, duration, name, color, visible, selected, parent)
        self._events = events or []

    def data(self):
        return {
            **AnnotationModel.data(self),
            "events": [event.data() for event in self._events]
        }

    @classmethod
    def parse(cls, data):
        timeline = cls(**{key: value for key, value in data.items() if key != "events"})
        for event in data['events']:
            timeline.add(EventModel.parse(event))
        return timeline

    def __len__(self) -> int:
        return len(self._events)

    def __getitem__(self, idx: int) -> EventModel:
        return self._events[idx]

    def in_range(self, first: int, last: int) -> List[EventModel]:
        return [event for event in self._events if event.intersects(first, last)]

    def at_frame_id(self, frame_id: int) -> EventModel|None:
        """ event where first <= frame_id <= last """
        for event in self._events:
            if frame_id in event:
                return event
        return None

    def before_frame_id(self, frame_id: int, default=None) -> EventModel|None:
        """ last event where last < frame_id """
        for event in self._events[::-1]:
            if event.last < frame_id:
                return event
        return default

    def after_frame_id(self, frame_id: int, default=None) -> EventModel|None:
        """ first event where first > frame_id """
        for event in self._events:
            if event.first > frame_id:
                return event
        return default

    def can_add(self, first: int, last: int) -> bool:
        assert last >= first
        if not (0 <= first): return False
        if not (last < self._duration): return False
        return not self.in_range(first, last)

    def add(self, event: EventModel) -> EventModel:
        assert self.can_add(event.first, event.last)
        event.setParent(self)
        prv     = self.before_frame_id(event.first,)
        event.set_prv_event(prv)
        nxt     = self.after_frame_id(event.last)
        event.set_nxt_event(nxt)
        self._insert_event(event)
        return event

    def _insert_event(self, event: EventModel):
        # update neighboors
        if isinstance(event.prv_event, EventModel):
            event.prv_event.set_nxt_event(event)
        if isinstance(event.nxt_event, EventModel):
            event.nxt_event.set_prv_event(event)
        # insert into the list (keep the list sorted)
        if event.nxt_event is None:
            index = len(self._events)
        else:
            index = self._events.index(event._nxt_event)
        # add to the list
        self._events.insert(index, event)
        self.event_added.emit(event)
        return event

    def remove(self, event: EventModel) -> EventModel:
        # update neighboors
        if isinstance(event.prv_event, EventModel):
            event.prv_event.set_nxt_event(event.nxt_event)
        if isinstance(event.nxt_event, EventModel):
            event.nxt_event.set_prv_event(event.prv_event)
        # remove from the list
        self._events.remove(event)
        self.event_removed.emit(event)
        # reset parent
        event.setParent(None)
        return event
