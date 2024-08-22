from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Tuple

class TimeseriesModel(QObject):
    def __init__(self, 
                 name: str, 
                 xy_values: List[Tuple[int|float, float]],
                 y_min: float, y_max: float,
                 duration: int,
                 parent: QObject | None=None):
        QObject.__init__(self, parent)
        self._duration      = duration
        self._name          = name
        self._xy_values     = xy_values
        self._ymin          = y_min
        self._ymax          = y_max

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.name}] #{self._xy_values}>"
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def xy_values(self) -> int:
        return self._xy_values

    @property
    def ymin(self) -> int:
        return self._ymin

    @property
    def ymax(self) -> int:
        return self._ymax

    def data(self):
        return {
            'name':         self._name,
            'xy_values':    self._xy_values,
            'y_min':        self._ymin,
            'y_max':        self._ymax,
        }
