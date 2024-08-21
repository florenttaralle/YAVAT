from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.timeseries import TimeseriesModel
from typing import List


class TimeseriesListModel(QObject):
    timeseries_added              = pyqtSignal(TimeseriesModel)
    "SIGNAL: timeline_added(timeseries: TimeseriesModel)"
    timeseries_removed            = pyqtSignal(TimeseriesModel)
    "SIGNAL: timeline_removed(timeseries: TimeseriesModel)"
    
    def __init__(self, duration: int, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._duration              = duration
        self._timeseries_list:      List[TimeseriesModel] = []
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} #{len(self._timeseries_list)}>"

    def __len__(self) -> int:
        return len(self._timeseries_list)

    def __getitem__(self, key: int|str) -> TimeseriesModel:
        if isinstance(key, str):
            key = self._timeseries_list.index(self.names())
        return self._timeseries_list[key]

    def names(self) -> List[str]:
        return [timeline.name for timeline in self._timelines]

    def clear(self):
        while len(self._timeseries_list):
            self.rem(self._timeseries_list[0])
    
    @property
    def duration(self) -> int:
        return self._duration

    def add(self, name, xy_values, y_min, y_max) -> TimeseriesModel:
        timeseries = TimeseriesModel(name, xy_values, y_min, y_max, self._duration)
        self._timeseries_list.append(timeseries)
        self.timeseries_added.emit(timeseries)
        return timeseries
    
    def rem(self, timeseries: TimeseriesModel) -> TimeseriesModel:
        self._timeseries_list.remove(timeseries)
        self.timeseries_removed.emit(timeseries)
        return timeseries

    def data(self):
        return [timeseries.data() for timeseries in self._timeseries_list]
