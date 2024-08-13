from .event import EventModel, QObject, pyqtSignal

class RangeEventModel(EventModel):
    duration_changed    = pyqtSignal(int)
    
    def __init__(self, prv_event: EventModel|int, nxt_event: EventModel|int, first: int, last: int, label: str="", parent: QObject | None=None):
        EventModel.__init__(self, prv_event, nxt_event, label, parent)
        self._first = first
        self._last = last
        
    @property
    def first(self) -> int:
        return self._first
    @first.setter
    def first(self, first: int):
        if first != self._first:
            self._first = first
            self.first_changed.emit(self._first)
            self.duration_changed.emit(self.duration)
    def setFirst(self, value: int):
        self.first = value

    @property
    def last(self) -> int:
        return self._last    
    @last.setter
    def last(self, last: int):
        if last != self._last:
            self._last = last
            self.last_changed.emit(self._last)
            self.duration_changed.emit(self.duration)
    def setLast(self, value: int):
        self.last = value

    @property
    def duration(self) -> int:
        return self._last - self._first

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.label}' @[{self.first};{self.last}] #{self.duration} >"
