from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List
import itertools as it
import attr
from src.models.annotation import AnnotationModel, QColor

@attr.define
class XYValue:
    x: float
    y: float

    def __len__(self) -> int: 
        return 2
    def __getitem__(self, idx: int) -> float: 
        return self.x if idx == 0 else self.y
    def __lt__(self, other: XYValue):
        return self.x < other.x
    
class TimeseriesModel(AnnotationModel):
    y_range_changed = pyqtSignal(float, float)
    "SIGNAL: yrange_changed(ymin: float, ymax: float)"

    next_id_generator = it.count()

    def __init__(self, duration: int, 
                 xy_values: List[XYValue], ymin: float, ymax: float,
                 name: str|None=None, color: QColor|str=None, 
                 visible: bool=True, selected: bool=False, parent: QObject|None=None):
        if name is None:
            name = f"Timeseries {next(self.next_id_generator)}"
        AnnotationModel.__init__(self, duration, name, color, visible, selected, parent)
        self._xy_values = sorted([XYValue(x, y) for x, y in (xy_values or [])])
        self._ymin      = ymin
        self._ymax      = ymax

    def data(self):
        return {
            **AnnotationModel.data(self),
            "ymin":         self._ymin,
            "ymax":         self._ymax,
            "xy_values":    [(xy_value.x, xy_value.y) for xy_value in self._xy_values]
        }

    @classmethod
    def parse(cls, data):
        return cls(**data)
    
    @property
    def xy_values(self) -> int:
        return self._xy_values

    @property
    def ymin(self) -> int:
        return self._ymin

    @property
    def ymax(self) -> int:
        return self._ymax

    def set_y_range(self, ymin: float, ymax: float):
        if ymin > ymax: return
        if (ymin != self._ymin) or (ymax != self._ymax):
            self._ymin = ymin
            self._ymax = ymax
            self.y_range_changed.emit(ymin, ymax)

    @property
    def X(self) -> List[float]:
        return [xy_value.x for xy_value in self._xy_values]
    
    @property
    def Y(self) -> List[float]:
        return [xy_value.y for xy_value in self._xy_values]
    
    