from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

class ColorListModel(QObject):
    color_changed = pyqtSignal(str, object)
    "SIGNAL: color_changed(name: str, color: QColor|None)"
    
    def __init__(self, colors: dict[str, QColor]=None, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._colors = {name: (QColor(color) if color is not None else None)
                        for name, color in (colors or {}).items()}

    def get(self, name: str) -> QColor|None:
        return self._colors.get(name, None)

    def __contains__(self, name: str) -> bool:
        return name in self._colors
        
    def __getitem__(self, name: str) -> QColor|None:
        return self._colors.get(name, None)

    def __setitem__(self, name: str, color: QColor|None):
        if color != self._colors.get(name):
            self._colors[name] = color
            self.color_changed.emit(name, color)

    def __delitem__(self, name: str):
        if name not in self._colors: return
        del self._colors[name]
        self.color_changed.emit(name, None)

    def serialize(self):
        return {
            name: (color.name() if color is not None else None)
            for name, color in self._colors.items()
        }

    @classmethod
    def parse(cls, data):
        return cls(**data)
    
    def update(self, colors: dict[str, QColor|None]) -> ColorListModel:
        self._colors.update(colors)
        return self
