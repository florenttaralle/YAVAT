from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Tuple

class EventModel(QObject):
    first_changed       = pyqtSignal(int)
    "SIGNAL: first_changed(first: int)"
    last_changed        = pyqtSignal(int)
    "SIGNAL: last_changed(last: int)"
    label_changed       = pyqtSignal(str)
    "SIGNAL: label_changed(label: str)"
    prv_event_changed   = pyqtSignal(object)
    "SIGNAL: prv_event_changed(event: EventModel|None)"
    nxt_event_changed   = pyqtSignal(object)
    "SIGNAL: nxt_event_changed(event: EventModel|None)"

    def __init__(self, first: int, last: int, prv_event: EventModel|None=None, nxt_event: EventModel|None=None, label: str="", parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._first     = first
        self._last      = last
        self._prv_event = prv_event
        self._nxt_event = nxt_event
        self._label     = label

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self._first} ; {self._last}] lbl:'{self._label}'>"
    
    def data(self):
        return {
            "first":    self._first,
            "last":     self._last,
            "label":    self._label,
        }
    
    @property
    def timeline(self):
        return self.parent()
    
    @classmethod
    def parse(cls, data):
        return cls(**data)
    
    @classmethod
    def parse(cls, data):
        return cls(**data)
    
    @property
    def label(self) -> str:
        return self._label
    def set_label(self, label: str):
        if label != self._label:
            self._label = label
            self.label_changed.emit(self._label)

    @property
    def first(self) -> int: 
        return self._first
    def set_first(self, first: int):
        if first != self._first:
            self._first = first
            self.first_changed.emit(first)

    @property
    def last(self) -> int: 
        return self._last
    def set_last(self, last: int):
        if last != self._last:
            self._last = last
            self.last_changed.emit(last)

    @property
    def first_min(self) -> int:
        return self._prv_event.last + 1 if self._prv_event else 0
    @property
    def first_max(self) -> int:
        return self._last

    @property
    def last_min(self) -> int:
        return self.first
    @property
    def last_max(self) -> int:
        return self._nxt_event.first - 1 if self._nxt_event else self.timeline.duration - 1

    @property
    def prv_event(self) -> EventModel|None:
        return self._prv_event
    def set_prv_event(self, event: EventModel|None):
        if event != self._prv_event:
            self._prv_event = event
            self.prv_event_changed.emit(self._label)

    @property
    def nxt_event(self) -> EventModel|int:
        return self._nxt_event
    def set_nxt_event(self, event: EventModel|int):
        if event != self._nxt_event:
            self._nxt_event = event
            self.nxt_event_changed.emit(self._label)

    def __contains__(self, frame_id: int) -> bool:
        return self.first <= frame_id <= self.last

    def union(self, first: int, last: int) -> Tuple[int, int]:
        union_first   = min(self.first, first)
        union_last    = max(self.last, last)
        return (union_first, union_last)
    
    def intersection(self, first: int, last: int) -> Tuple[int, int]|None:
        inter_first   = max(self.first, first)
        inter_last    = min(self.last, last)
        return (inter_first, inter_last) if inter_last >= inter_first else None

    def intersects(self, first: EventModel|int, last: None|int=None) -> bool:
        if isinstance(first, EventModel) and last is None:
            self.intersects(first.first, first.last)
        elif isinstance(first, int) and isinstance(last, int):
            return bool(self.intersection(first, last))
        raise TypeError()

    def move_to(self, new_timeline):
        if new_timeline != self.timeline:
            assert new_timeline.can_add(self.first, self.last)
            self.timeline.remove(self)
            new_timeline.add(self)
        return self

    def remove(self):
        self.timeline.remove(self)
