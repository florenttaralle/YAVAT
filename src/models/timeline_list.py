from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.timeline import TimeLineModel
from typing import List
import itertools as it


class TimeLineListModel(QObject):
    timeline_added          = pyqtSignal(TimeLineModel)
    timeline_removed        = pyqtSignal(TimeLineModel)    
    _nxt_item_id            = it.count()
    
    def __init__(self, duration: int, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._duration = duration
        self._items: List[TimeLineModel] = []
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} #{len(self)}>"

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, key: int|str) -> TimeLineModel:
        if isinstance(key, str):
            key = self._items.index(self._names())
        return self._items[key]

    def _names(self) -> List[str]:
        return [item.name for item in self._items]
    
    def __contains__(self, name: str):
        return name in self._names()
    
    def add(self, name: str|None=None) -> TimeLineModel:
        if name is None:
            name = self._gen_item_name()
        else:
            assert name not in self
        timeline = TimeLineModel(self._duration, name)
        self._items.append(timeline)
        self.timeline_added.emit(timeline)
        return timeline
    
    @classmethod
    def _gen_item_name(cls) -> str:
        return f"TimeLine {next(cls._nxt_item_id)}"
    
    def rem(self, timeline: TimeLineModel) -> TimeLineModel:
        self._items.remove(timeline)
        self.timeline_removed.emit(timeline)
        return timeline
    