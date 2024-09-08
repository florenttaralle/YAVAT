from PyQt6.QtWidgets import QWidget
# ##################################################################
from src.models.time_window import TimeWindowModel
from src.models.timeseries import TimeseriesModel
from src.models.annotation_watchers import AnnotationWatcherSingleton, AnnotationValueWatcherModel
from src.views.annotation import AnnotationView, AnnotationHeaderView
from src.views.timeseries_graph import TimeseriesGraphView
from src.views.contextual_menus.time_window import TimeWindowContextualMenu, QMenu, QCursor
# ##################################################################


class TimeseriesView(AnnotationView):
    def __init__(self, timeseries: TimeseriesModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        header  = AnnotationHeaderView(timeseries, True)
        graph   = TimeseriesGraphView(time_window, timeseries)
        AnnotationView.__init__(self, timeseries, time_window, header, graph, parent)
        self._watcher = AnnotationWatcherSingleton.get_or_create(
            AnnotationValueWatcherModel, timeseries, time_window)
        self._watcher.value_changed.connect(self.onValueChanged)
        self._set_value(self._watcher.value)

    @property
    def timeseries(self) -> TimeseriesModel:
        return self._annotation
    
    def _set_value(self, value: float|None):
        self._header._value_lbl.setText(str(round(value, 2) or "NaN") + " >")
    
    def onValueChanged(self, timeseries: TimeseriesModel, frame_id: int, value: float|None):
        self._set_value(value)

    def onGraphContextMenu(self, frame_id: int, cm_event):
        AnnotationView.onGraphContextMenu(self, frame_id, cm_event)
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        menu    = QMenu()
        tw_menu = TimeWindowContextualMenu(self._time_window, frame_id).attach(menu)
        menu.exec(QCursor.pos())
    
    def onGraphDoubleClick(self, frame_id: int, m_event):
        AnnotationView.onGraphDoubleClick(self, frame_id, m_event)
