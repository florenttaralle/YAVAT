from __future__ import annotations
import attr

from PyQt6.QtCore import pyqtSignal

from .annotation import AnnotationModel, QColor

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

    def __init__(self, duration: int, name: str, color: QColor, 
                 xy_values: list[tuple[float, float]], ymin: float, ymax: float):
        AnnotationModel.__init__(self, duration, name, color)
        self._xy_values = sorted([XYValue(x, y) for x, y in xy_values])
        self._ymin      = ymin
        self._ymax      = ymax

    def serialize(self):
        return {
            **AnnotationModel.serialize(self),
            "xy_values":    [(xy_value.x, xy_value.y) for xy_value in self._xy_values],
            "ymin":         self._ymin,
            "ymax":         self._ymax,
        }

    @classmethod
    def parse(cls, duration: int, name: str, color: str, xy_values, ymin, ymax):
        return cls(duration, name, color, xy_values, ymin, ymax)
    
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
    def X(self) -> list[float]:
        return [xy_value.x for xy_value in self._xy_values]
    
    @property
    def Y(self) -> list[float]:
        return [xy_value.y for xy_value in self._xy_values]
    
    