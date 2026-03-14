from typing import Generic, TypeVar

from PyQt6.QtCore import QObject, pyqtSignal

T = TypeVar("T")

class WatchedItemModel(QObject, Generic[T]):
    before_changed = pyqtSignal(object, object)
    "SIGNAL: before_changed(prv: T|None, new: T|None)"
    
    changed = pyqtSignal(object)
    "SIGNAL: changed(new: T|None)"
    
    def __init__(self, initial: T|None=None, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._item = initial
    
    @property
    def item(self) -> T|None:
        return self._item

    def get(self) -> T|None:
        return self._item

    def set(self, new_item: T|None):
        if self._item != new_item:
            prv_item = self._item
            self.before_changed.emit(prv_item, new_item)
            self._item = new_item
            self.changed.emit(new_item)
