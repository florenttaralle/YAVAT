from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

class AnnotationModel(QObject):
    name_changed = pyqtSignal(str)
    "SIGNAL: name_changed(name: str)"
    color_changed = pyqtSignal(QColor)
    "SIGNAL: color_changed(color: QColor)"
    visible_changed = pyqtSignal(bool)
    "SIGNAL: visible_changed(visible: bool)"
    selected_changed = pyqtSignal(bool)
    "SIGNAL: selected_changed(selected: bool)"

    DEFAULT_COLOR = "#346beb"
    
    def __init__(self, duration: int, name: str, color: QColor|str=None, visible: bool=True, selected: bool=False, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._duration  = duration
        self._name      = name
        self._color     = QColor(color or self.DEFAULT_COLOR)
        self._visible   = visible
        self._selected  = selected

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.name}|{self._color.name()}] #{self._duration} v:{self._visible} s:{self._selected}>"

    def data(self):
        return {
            "type":         self.__class__.__name__,
            "duration":     self._duration,
            "name":         self._name,
            "color":        self._color.name(),
            "visible":      self._visible,
            "selected":     self._selected
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
    
    @property
    def visible(self):
        return self._visible
    def set_visible(self, visible: bool):
        if visible != self._visible:
            self._visible = visible
            self.visible_changed.emit(visible)
    
    @property
    def selected(self):
        return self._selected
    def set_selected(self, selected: bool):
        if selected != self._selected:
            self._selected = selected
            self.selected_changed.emit(selected)
