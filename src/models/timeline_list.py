from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.timeline import TimelineModel
from typing import List
import itertools as it


class TimelineListModel(QObject):
    timeline_added              = pyqtSignal(TimelineModel)
    "SIGNAL: timeline_added(timeline: TimelineModel)"
    timeline_removed            = pyqtSignal(TimelineModel)
    "SIGNAL: timeline_removed(timeline: TimelineModel)"
    duration_changed            = pyqtSignal(int)
    "SIGNAL: duration_changed(duration: int)"
    _nxt_item_id                = it.count()
    
    def __init__(self, duration: int, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._duration              = duration
        self._timelines:            List[TimelineModel] = []
        self._selected_timeline:    TimelineModel|None = None
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} #{len(self._timelines)}>"

    def __len__(self) -> int:
        return len(self._timelines)

    def __getitem__(self, key: int|str) -> TimelineModel:
        if isinstance(key, str):
            key = self._timelines.index(self.names())
        return self._timelines[key]

    def names(self) -> List[str]:
        return [timeline.name for timeline in self._timelines]

    def clear(self):
        while len(self._timelines):
            self.rem(self._timelines[0])
    
    @property
    def duration(self) -> int:
        return self._duration
    @duration.setter
    def duration(self, duration: int):
        self.set_duration(duration)
    def set_duration(self, duration: int):
        if duration != self._duration:
            assert len(self) == 0, 'Cant update duration when timelines exist'
            self._duration = duration
            self.duration_changed.emit(duration)

    def __contains__(self, name: str) -> bool:
        return name in self.names()
    
    def add(self, name: str|None=None) -> TimelineModel:
        if name is None:
            name = self._gen_item_name()
        else:
            assert name not in self
        timeline = TimelineModel(self._duration, name)
        self._timelines.append(timeline)
        self.timeline_added.emit(timeline)
        return timeline
    
    @classmethod
    def _gen_item_name(cls) -> str:
        return f"Timeline {next(cls._nxt_item_id)}"
    
    def rem(self, timeline: TimelineModel) -> TimelineModel:
        self._timelines.remove(timeline)
        self.timeline_removed.emit(timeline)
        return timeline

    def data(self):
        return [timeline.data() for timeline in self._timelines]

    def flat_data(self):
        return list(it.chain(*[timeline.flat_data() for timeline in self._timelines]))

