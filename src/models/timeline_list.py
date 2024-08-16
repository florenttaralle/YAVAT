from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.timeline import TimeLineModel
from typing import List
import itertools as it


class TimeLineListModel(QObject):
    timeline_added              = pyqtSignal(TimeLineModel)
    timeline_removed            = pyqtSignal(TimeLineModel)
    selected_timeline_changed   = pyqtSignal(object, object) # (TimeLineModel|None, TimeLineModel|None)
    _nxt_item_id                = it.count()
    
    def __init__(self, duration: int, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._duration              = duration
        self._items:                List[TimeLineModel] = []
        self._selected_timeline:    TimeLineModel|None = None
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} #{len(self)}>"

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, key: int|str) -> TimeLineModel:
        if isinstance(key, str):
            key = self._items.index(self._names())
        return self._items[key]

    @property
    def selected_timeline(self) -> TimeLineModel|None:
        return self._selected_timeline
    @selected_timeline.setter
    def selected_timeline(self, timeline: TimeLineModel|None):
        if timeline != self._selected_timeline:
            previous_timeline = self._selected_timeline
            self._selected_timeline = timeline
            self.selected_timeline_changed.emit(timeline, previous_timeline)

    def _names(self) -> List[str]:
        return [item.name for item in self._items]
    
    def __contains__(self, name: str):
        return name in self._names()
    
    def add(self, name: str|None=None, select: bool=True) -> TimeLineModel:
        if name is None:
            name = self._gen_item_name()
        else:
            assert name not in self
        timeline = TimeLineModel(self._duration, name)
        self._items.append(timeline)
        self.timeline_added.emit(timeline)
        if select:
            self.selected_timeline = timeline
        return timeline
    
    @classmethod
    def _gen_item_name(cls) -> str:
        return f"TimeLine {next(cls._nxt_item_id)}"
    
    def rem(self, timeline: TimeLineModel) -> TimeLineModel:
        if timeline is self._selected_timeline:
            self.selected_timeline = None
        self._items.remove(timeline)
        self.timeline_removed.emit(timeline)
        return timeline
