from __future__ import annotations
from PyQt6.QtCore import QObject
from src.models.annotation import AnnotationModel

class AnnotationWatcherModel(QObject):
    def __init__(self, annotation: AnnotationModel):
        QObject.__init__(self, annotation)
        self.annotation = annotation
