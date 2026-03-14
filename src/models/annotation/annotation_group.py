from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

from .annotation import AnnotationModel
from .annotation_factory import annotation_factory

class AnnotationGroupModel(AnnotationModel):
    item_attached   = pyqtSignal(QObject, int)
    "SIGNAL: item_attached(item: AnnotationGroupModel|AnnotationModel, pos: int)"
    item_detached   = pyqtSignal(QObject, int)
    "SIGNAL: item_detached(item: AnnotationGroupModel|AnnotationModel, pos: int)"
    item_moved          = pyqtSignal(QObject, int, int)
    "SIGNAL: item_moved(item: AnnotationGroupModel|AnnotationModel, prv_pos: int, new_pos: int)"

    def __init__(self, duration: int, name: str, color: QColor, items: list[AnnotationModel]|None=None):
        AnnotationModel.__init__(self, duration, name, color) 
        self._items: list[AnnotationModel] = items or []

    def attach(self, item: AnnotationGroupModel|AnnotationModel, pos: int|None=None):
        pos = pos if pos is not None else len(self)
        self._items.insert(pos, item)
        self.item_attached.emit(item, pos)
    
    def detach(self, item: AnnotationGroupModel|AnnotationModel):
        pos = self._items.index(item)
        self._items.remove(item)
        self.item_detached.emit(item, pos)
    
    def move(self, crt_pos: int, new_pos: int):
        if crt_pos == new_pos:
            return
        item = self._items[crt_pos]
        self._items.insert(new_pos, self._items.pop(crt_pos))
        self.item_moved.emit(item, crt_pos, new_pos)
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __getitem__(self, idx: int) -> AnnotationGroupModel|AnnotationModel:
        return self._items[idx]
    
    def serialize(self):
        return {
            **AnnotationModel.serialize(self),
            "items": [item.serialize() for item in self._items]
        }

    @classmethod
    def parse(cls, duration: int, name: str, color: str, items: list):
        items = [annotation_factory(**item) for item in items]
        return cls(duration, name, color, items)
