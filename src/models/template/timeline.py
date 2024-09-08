from __future__ import annotations
from PyQt6.QtGui import QColor
import attr
from typing import Mapping
from src.models.timeline import TimelineModel, AnnotationModel


@attr.define
class TimelineTemplateModel:
    name:   str
    color:  QColor|None = None
    colors: Mapping[str, QColor|None] = attr.field(factory=list)

    def data(self):
        data = {'name': self.name}
        if self.color is not None:
            data.update({'color': self.color.name()})
        return data

    def apply(self, annotation: AnnotationModel) -> bool:
        if isinstance(annotation, TimelineModel) and (annotation.name == self.name):
            if self.color is not None:
                annotation.set_color(self.color)
            annotation.colors.update(self.colors)
            return True
        else:
            return False

    @classmethod
    def parse(cls, data) -> TimelineTemplateModel:
        name = data.get("name", "")
        color = data.get("color", None)
        if color is not None:
            color = QColor(color)
        colors = data.get("colors", {})
        return cls(name, color, colors)

    @classmethod
    def from_timeline(cls, timeline: TimelineModel) -> TimelineTemplateModel:
        return cls(timeline.name, timeline.color, timeline.colors.data())
