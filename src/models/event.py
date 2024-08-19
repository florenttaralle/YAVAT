from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Tuple

class EventModel(QObject):
    label_changed       = pyqtSignal(str)
    "SIGNAL: label_changed(label: str)"
    first_changed       = pyqtSignal(int)
    "SIGNAL: first_changed(first: int)"
    last_changed        = pyqtSignal(int)
    "SIGNAL: last_changed(last: int)"
    prv_event_changed   = pyqtSignal(object)
    "SIGNAL: prv_event_changed(event: EventModel|int)"
    nxt_event_changed   = pyqtSignal(object)
    "SIGNAL: nxt_event_changed(event: EventModel|int)"

    def __init__(self, first: int, last: int, prv_event: EventModel|int, nxt_event: EventModel|int, label: str="", parent: QObject | None=None):
        QObject.__init__(self, parent)
        self._first     = first
        self._last      = last
        self._prv_event = prv_event
        self._nxt_event = nxt_event
        self._label     = label

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self._first} ; {self._last}] lbl:'{self._label}'>"
    
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
        return self._first
    @first.setter
    def first(self, first: int):
        if first != self._first:
            self._first = first
            self.first_changed.emit(first)
    def set_first(self, first: int):
        self.first = first

    @property
    def last(self) -> int: 
        return self._last
    @last.setter
    def last(self, last: int):
        if last != self._last:
            self._last = last
            self.last_changed.emit(last)
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

    def intersects(self, first: EventModel|int, last: None|int=None) -> bool:
        if isinstance(first, EventModel) and last is None:
            self.intersects(first.first, first.last)
        elif isinstance(first, int) and isinstance(last, int):
            return bool(self.intersection(first, last))
        raise TypeError()
    
    def data(self):
        return {
            'first':    self._first,
            'last':     self._last,
            'label':    self._label,
        }