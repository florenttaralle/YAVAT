from .event import EventModel, QObject, pyqtSignal

class PonctualEventModel(EventModel):
    frame_id_changed = pyqtSignal(int)
    
    def __init__(self, prv_event: EventModel|int, nxt_event: EventModel|int, frame_id: int, label: str="", parent: QObject | None=None):
        EventModel.__init__(self, prv_event, nxt_event, label, parent)
        self._frame_id = frame_id

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.label}' @{self.frame_id} >"

    @property
    def frame_id(self) -> int:
        return self._frame_id

    @frame_id.setter
    def frame_id(self, frame_id: int):
        if frame_id != self._frame_id:
            self._frame_id = frame_id
            self.frame_id_changed.emit(self._frame_id)
            self.first_changed.emit(self._frame_id)
            self.last_changed.emit(self._frame_id)

    @property
    def first(self) -> int: 
        return self._frame_id
    @first.setter
    def first(self, first: int):
        self.frame_id = first
    
    @property
    def last(self) -> int: 
        return self._frame_id
    @last.setter
    def last(self, last: int):
        self.frame_id = last

