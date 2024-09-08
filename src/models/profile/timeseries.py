from __future__ import annotations
from PyQt6.QtGui import QColor
import attr
from src.models.timeseries import TimeseriesModel, AnnotationModel


@attr.define
class TimeseriesProfileModel:
    name:   str
    color:  QColor|None = None
    ymin:   float|None = None
    ymax:   float|None = None

    def data(self):
        data = {
            'name':     self.name,
            'color':    self.color.name() if self.color is not None else None,
            'ymin':     self.ymin,
            'ymax':     self.ymax,
        }
        return data

    def apply(self, annotation: AnnotationModel) -> bool:
        if isinstance(annotation, TimeseriesModel) and (annotation.name == self.name):
            if self.color is not None:
                annotation.set_color(self.color)
                
            if (self.ymin is not None) and (self.ymax is not None):
                annotation.set_y_range(self.ymin, self.ymax)
                
            return True
        else:
            return False

    @classmethod
    def parse(cls, data) -> TimeseriesProfileModel:
        name    = data.get("name", "")
        color   = data.get("color", None)
        if color is not None:
            color = QColor(color)
        ymin    = data.get('ymin', None)
        ymax    = data.get('ymax', None)
        return cls(name, color, ymin, ymax)

    @classmethod
    def from_timeseries(cls, timeseries: TimeseriesModel) -> TimeseriesProfileModel:
        return cls(timeseries.name, timeseries.color, timeseries.ymin, timeseries.ymax)
