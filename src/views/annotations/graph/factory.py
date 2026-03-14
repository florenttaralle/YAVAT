from PyQt6.QtCore import QObject

from src.models.annotation import AnnotationModel, TimeseriesModel, TimelineModel
from src.models.time_window import TimeWindowModel
from .graph import GraphView
from .timeline import TimelineGraphView
from .timeseries import TimeseriesGraphView

def graph_view_factory(annotation: AnnotationModel, time_window: TimeWindowModel, parent: QObject|None=None) -> GraphView|None:
    if isinstance(annotation, TimelineModel):
        return TimelineGraphView(time_window, annotation, parent)
    
    if isinstance(annotation, TimeseriesModel):
        return TimeseriesGraphView(time_window, annotation, parent)
    
    return None
