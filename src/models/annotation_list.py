from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List
from src.models.annotation import AnnotationModel
from src.models.timeline import TimelineModel
from src.models.timeseries import TimeseriesModel

class AnnotationListModel(QObject):
    item_added          = pyqtSignal(AnnotationModel)
    "SIGNAL: item_added(annotation: AnnotationModel)"
    item_removed        = pyqtSignal(AnnotationModel)
    "SIGNAL: item_removed(annotation: AnnotationModel)"
    selected_changed    = pyqtSignal(object)
    "SIGNAL: selected_changed(annotation: AnnotationModel|None)"
    item_moved          = pyqtSignal(AnnotationModel, int, int)
    "SIGNAL: item_moved(annotation: AnnotationModel, prv_index: int, new_index: int)"    

    def __init__(self, duration: int, annotations: List[AnnotationModel]=None, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._duration = duration
        self._annotations: List[AnnotationModel] = []
        self._selected: AnnotationModel|None = None
        for annotation in annotations or []:
            self.append(annotation)

    def data(self):
        return [annotation.data() for annotation in self._annotations]

    @property
    def duration(self) -> int:
        return self._duration

    @classmethod
    def parse(cls, duration: int, data):
        def factory(data_):
            if data_['type'] == TimelineModel.__name__:
                return TimelineModel.parse({k:v for k, v in data_.items() if k != "type"})
            else:
                return TimeseriesModel.parse({k:v for k, v in data_.items() if k != "type"})
        return cls(duration, [factory(annotation) for annotation in data])

    @property
    def selected(self) -> AnnotationModel|None:
        return self._selected
    def set_selected(self, selected: AnnotationModel|None):
        if selected != self._selected:
            if self._selected is not None:
                self._selected.set_selected(False)
            self._selected = selected
            if self._selected is not None:
                self._selected.set_selected(True)
            self.selected_changed.emit(selected)
    
    def __len__(self) -> int:
        return len(self._annotations)

    def __getitem__(self, idx: int) -> AnnotationModel:
        return self._annotations[idx]

    def append(self, item: AnnotationModel) -> AnnotationModel:
        return self.insert(item, len(self._annotations))
    
    def insert(self, item: AnnotationModel, index: int) -> AnnotationModel:
        item.setParent(self)
        self._annotations.insert(index, item)
        self.item_added.emit(item)
        item.selected_changed.connect(lambda selected: self.onItemSelectedChanged(item, selected))
        if item.selected: 
            self.set_selected(item)
        return item

    def remove(self, item: AnnotationModel) -> AnnotationModel:
        item.setParent(None)
        if item == self._selected:
            self.set_selected(None)
        self._annotations.remove(item)
        self.item_removed.emit(item)
        return item

    def move(self, item: AnnotationModel, index: int) -> AnnotationModel:
        crt_index = self._annotations.index(item)
        if index != crt_index:
            self._annotations.insert(index, self._annotations.pop(crt_index))
            self.item_moved.emit(item, crt_index, index)

    def index(self, item: AnnotationModel):
        return self._annotations.index(item)

    def move_up(self, item: AnnotationModel):
        index = self._annotations.index(item)
        if index > 0:
            self.move(item, index - 1)
    
    def move_down(self, item: AnnotationModel):
        index = self._annotations.index(item)
        if index < len(self._annotations) - 1:
            self.move(item, index + 1)

    def onItemSelectedChanged(self, item: AnnotationModel, selected: bool):
        if selected:
            self.set_selected(item)
        else:
            if item == self._selected:
                self.set_selected(None)

