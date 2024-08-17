from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Tuple

class EventModel(QObject):
    label_changed       = pyqtSignal(str)
    first_changed       = pyqtSignal(int)
    last_changed        = pyqtSignal(int)
    prv_event_changed   = pyqtSignal(object) # EventModel|int
    nxt_event_changed   = pyqtSignal(object) # EventModel|int

    def __init__(self, prv_event: EventModel|int, nxt_event: EventModel|int, label: str="", parent: QObject | None=None):
        QObject.__init__(self, parent)
        self._prv_event = prv_event
        self._nxt_event = nxt_event
        self._label = label

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.label}' >"
        
    @property
    def label(self) -> str:
        return self._label
    @label.setter
    def label(self, label: str):
        if label != self._label:
            self._label = label
            self.label_changed.emit(self._label)

    @property
    def prv_event(self) -> EventModel|int:
        return self._prv_event
    @prv_event.setter
    def prv_event(self, event: EventModel|int):
        if event != self._prv_event:
            self._prv_event = event
            self.prv_event_changed.emit(self._label)

    @property
    def nxt_event(self) -> EventModel|int:
        return self._nxt_event
    @nxt_event.setter
    def nxt_event(self, event: EventModel|int):
        if event != self._nxt_event:
            self._nxt_event = event
            self.nxt_event_changed.emit(self._label)

    @property
    def first(self) -> int: 
        raise NotImplementedError()
    
    @property
    def last(self) -> int: 
        raise NotImplementedError()

    def set_first(self, first: int):
        self.first = first

    def set_last(self, last: int):
        self.last = last
        

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

    def intersects(self, first: int, last: int) -> bool:        
        return bool(self.intersection(first, last))
