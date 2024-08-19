from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List
from .event import EventModel

class TimelineModel(QObject):
    duration_changed    = pyqtSignal(int)
    "SIGNAL: duration_changed(duration: int)"
    name_changed        = pyqtSignal(str)
    "SIGNAL: name_changed(name: str)"
    event_added         = pyqtSignal(EventModel)
    "SIGNAL: event_added(event: EventModel)"
    event_removed       = pyqtSignal(EventModel)
    "SIGNAL: event_removed(event: EventModel)"
    
    def __init__(self, duration: int, name: str, parent: QObject | None=None):
        QObject.__init__(self, parent)
        self._duration                  = duration
        self._name                      = name
        self._events: List[EventModel]  = []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.name}] #{len(self)}>"
    
    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, name: str):
        if name != self._name:
            self._name = name
            self.name_changed.emit(self._name)

    @property
    def duration(self) -> int:
        return self._duration

    def __len__(self) -> int:
        return len(self._events)

    def __getitem__(self, idx: int) -> EventModel:
        return self._events[idx]

    def at_frame_id(self, frame_id: int) -> EventModel|None:
        """ event where first <= frame_id <= last """
        for event in self._events:
            if frame_id in event:
                return event
        return None

    def in_range(self, first: int, last: int) -> List[EventModel]:
        return [event for event in self._events if event.intersects(first, last)]

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

    def add(self, first: int, last: int, label: str="", parent: QObject|None=None) -> EventModel:
        assert self.can_add(first, last)
        prv     = self.before_frame_id(first, 0)
        nxt     = self.after_frame_id(last, self._duration-1)
        event   = EventModel(first, last, prv, nxt, label, parent)
        self._insert_event(event)
        return event

    def _insert_event(self, event: EventModel):
        # update neighboors
        if isinstance(event.prv_event, EventModel):
            event.prv_event.nxt_event = event
        if isinstance(event.nxt_event, EventModel):
            event.nxt_event.prv_event = event
        # insert into the list (keep the list sorted)
        if isinstance(event.nxt_event, int):
            index = len(self._events)
        else:
            index = self._events.index(event._nxt_event)
        self._events.insert(index, event)
        self.event_added.emit(event)
        return event

    def rem(self, event: EventModel) -> EventModel:
        # update neighboors
        if isinstance(event.prv_event, EventModel):
            event.prv_event.nxt_event = event.nxt_event
        if isinstance(event.nxt_event, EventModel):
            event.nxt_event.prv_event = event.prv_event
        # remove for the list
        self._events.remove(event)
        self.event_removed.emit(event)
        return event
