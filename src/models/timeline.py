from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List
from .event import EventModel
from .ponctual_event import PonctualEventModel
from .range_event import RangeEventModel

class TimeLineModel(QObject):
    duration_changed    = pyqtSignal(int)
    name_changed        = pyqtSignal(str)
    event_added         = pyqtSignal(EventModel)
    event_removed       = pyqtSignal(EventModel)
    
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
    @duration.setter
    def duration(self, duration: int):
        if duration != self._duration:
            assert duration > 0
            assert all([event.last <= duration for event in self._events]) # TODO: clean invalid items
            self._duration = duration
            self.duration_changed.emit(self._duration)

    def __len__(self) -> int:
        return len(self._events)

    def __getitem__(self, key: int) -> EventModel:
        return self._events[key]

    def before_event(self, event: EventModel) -> EventModel|None:
        crt_index = self._events.index(event)
        if crt_index > 0:
            return self._events[crt_index - 1]
        else:
            return None

    def after_event(self, event: EventModel) -> EventModel|None:
        crt_index = self._events.index(event)
        if crt_index < len(self._events) - 1:
            return self._events[crt_index + 1]
        else:
            return None

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

    def can_add_ponctual(self, frame_id: int) -> bool:
        return (0 <= frame_id <= self._duration) \
            and all([not event.intersects(frame_id, frame_id) for event in self._events])

    def add_ponctual(self, frame_id: int, label: str="") -> PonctualEventModel:
        assert self.can_add_ponctual(frame_id)
        prv     = self.before_frame_id(frame_id, 0)
        nxt     = self.after_frame_id(frame_id, self._duration)
        event   = PonctualEventModel(prv, nxt, frame_id, label)
        self._insert_event(event)
        return event

    def can_add_range(self, first: int, last: int|None = None) -> bool:
        if last is None:
            last = first + 1
        return (0 <= first <= self._duration) \
            and (0 <= last <= self._duration) \
            and (first < last) \
            and all([not event.intersects(first, last) for event in self._events])

    def add_range(self, first: int, last: int|None = None, label: str="") -> RangeEventModel:
        if last is None:
            last = first + 1
        assert self.can_add_range(first, last)
        prv     = self.before_frame_id(first, 0)
        nxt     = self.after_frame_id(last, self._duration)
        event   = RangeEventModel(prv, nxt, first, last, label)
        self._insert_event(event)
        return event

    def can_to_ponctual(self, event: EventModel, frame_id: int) -> bool:
        if not isinstance(event, RangeEventModel): return False
        return frame_id in event

    def to_ponctual(self, event: EventModel, frame_id: int) -> PonctualEventModel:
        assert self.can_to_ponctual(event, frame_id)
        self.rem(event)
        return self.add_ponctual(frame_id, event.label)

    def can_to_range(self, event: EventModel, frame_id: int) -> bool:
        if not isinstance(event, PonctualEventModel): return False
        if frame_id == self._duration -1: return False
        return (frame_id in event) and (
            ((frame_id + 1) <= event.last) or 
            isinstance(event.nxt_event, int) or
            ((frame_id + 1) < event.nxt_event.first)
        )

    def to_range(self, event: EventModel, frame_id: int) -> RangeEventModel:
        assert self.can_to_range(event, frame_id)
        self.rem(event)
        return self.add_range(frame_id, frame_id + 1, event.label)

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
