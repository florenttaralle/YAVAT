from __future__ import annotations
from PyQt6.QtCore import QObject
from typing import List
import itertools as it
import attr
from src.models.annotation import AnnotationModel, QColor

@attr.define
class XYValue:
    x: float
    y: float

class TimeseriesModel(AnnotationModel):
    next_id_generator = it.count()

    def __init__(self, duration: int, name: str|None=None, color: QColor|str=None, visible: bool=True, selected: bool=False, 
                 xy_values: List[XYValue]=None, ymin: float=0, ymax: float=1, parent: QObject|None=None):
        if name is None:
            name = f"Timeseries {next(self.next_id_generator)}"
        AnnotationModel.__init__(self, duration, name, color, visible, selected, parent)
        self._xy_values = xy_values or []
        self._ymin      = ymin
        self._ymax      = ymax

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.name}] #{self._xy_values}>"

    def data(self):
        return {
            **AnnotationModel.data(self),
            "ymin":         self._ymin,
            "ymax":         self._ymax,
            "xy_values":    [(xy_value.x, xy_value.y) for xy_value in self._xy_values]
        }

    @classmethod
    def parse(cls, data):
        return cls(
            xy_values = [XYValue(*xy_value) for xy_value in data['xy_values']],
            **{key: value for key, value in data.items() if key != 'xy_values'},
        )        
    
    @property
    def xy_values(self) -> int:
        return self._xy_values

    @property
    def ymin(self) -> int:
        return self._ymin

    @property
    def ymax(self) -> int:
        return self._ymax

    @property
    def X(self) -> List[float]:
        return [xy_value.x for xy_value in self._xy_values]
    
    @property
    def Y(self) -> List[float]:
        return [xy_value.y for xy_value in self._xy_values]
    
    