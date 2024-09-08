from PyQt6.QtCore import *
from .annotation_watcher import AnnotationWatcherModel, AnnotationModel

class AnnotationNameWatcher(AnnotationWatcherModel):
    name_changed = pyqtSignal(AnnotationModel, str)
    "SIGNAL: name_changed(annotation: AnnotationModel, name: str)"

    def __init__(self, annotation: AnnotationModel):
        AnnotationWatcherModel.__init__(self, annotation)
        self.annotation.name_changed.connect(self.onNameChanged)

    def onNameChanged(self, name: str):
        self.name_changed.emit(self.annotation, name)
