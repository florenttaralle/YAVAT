from PyQt6.QtWidgets import QWidget
from src.models.annotation import AnnotationModel
from src.models.timeline import TimelineModel
from src.models.timeseries import TimeseriesModel
from .timeline_editor import TimelineEditorDialog
from .timeseries_editor import TimeseriesEditorDialog

def exec_annotation_dialog(annotation: AnnotationModel, parent: QWidget|None=None) -> bool:
    if isinstance(annotation, TimelineModel):
        return TimelineEditorDialog(parent).exec(annotation)
    elif isinstance(annotation, TimeseriesModel):
        return TimeseriesEditorDialog(parent).exec(annotation)
