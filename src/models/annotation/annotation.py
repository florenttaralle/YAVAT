from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

class AnnotationModel(QObject):
    name_changed = pyqtSignal(str)
    "SIGNAL: name_changed(name: str)"
    color_changed = pyqtSignal(QColor)
    "SIGNAL: color_changed(color: QColor)"

    def __init__(self, duration: int, name: str, color: QColor):
        QObject.__init__(self)
        self._duration  = duration
        self._name      = name
        self._color     = color

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.name}|{self._color.name()}] #{self._duration}>"

    def serialize(self):
        return {
            "type":         self.__class__.__name__,
            "duration":     self._duration,
            "name":         self._name,
            "color":        self._color.name()
        }

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def name(self):
        return self._name
    def set_name(self, name: str):
        if name != self._name:
            self._name = name
            self.name_changed.emit(name)

    @property
    def color(self):
        return self._color
    def set_color(self, color: QColor):
        if color != self._color:
            self._color = color
            self.color_changed.emit(color)
