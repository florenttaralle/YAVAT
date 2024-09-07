from PyQt6.QtCore import *
from src.models.annotation import AnnotationModel

class AnnotationNameWatcher(QObject):
    name_changed = pyqtSignal(AnnotationModel, str)
    "SIGNAL: name_changed(annotation: AnnotationModel, name: str)"

    def __init__(self, annotation: AnnotationModel, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._annotation = annotation
        self._annotation.name_changed.connect(self.onNameChanged)

    def onNameChanged(self, name: str):
        self.name_changed.emit(self._annotation, name)
