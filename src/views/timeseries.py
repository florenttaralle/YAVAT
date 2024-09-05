from PyQt6.QtWidgets import QWidget
import numpy as np
# ##################################################################
from src.models.time_window import TimeWindowModel
from src.models.timeseries import TimeseriesModel
from src.views.annotation import AnnotationView, AnnotationHeaderView
from src.views.timeseries_graph import TimeseriesGraphView
from src.views.contextual_menus.time_window import TimeWindowContextualMenu, QMenu, QCursor
# ##################################################################


class TimeseriesView(AnnotationView):
    def __init__(self, timeseries: TimeseriesModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        header  = AnnotationHeaderView(timeseries, True)
        graph   = TimeseriesGraphView(time_window, timeseries)
        AnnotationView.__init__(self, timeseries, time_window, header, graph, parent)
        self._set_value()
        self._time_window.position_changed.connect(lambda *_: self._set_value())

    @property
    def timeseries(self) -> TimeseriesModel:
        return self._annotation
    
    def _set_value(self):
        idx     = np.argwhere(np.array(self.timeseries.X) == self._time_window.position)[0][0]
        value   = round(self.timeseries.Y[idx], 2)
        self._header._value_lbl.setText(str(value))
    
    def onGraphContextMenu(self, frame_id: int, cm_event):
        AnnotationView.onGraphContextMenu(self, frame_id, cm_event)
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        menu    = QMenu()
        tw_menu = TimeWindowContextualMenu(self._time_window, frame_id).attach(menu)
        menu.exec(QCursor.pos())
    
    def onGraphDoubleClick(self, frame_id: int, m_event):
        AnnotationView.onGraphDoubleClick(self, frame_id, m_event)
