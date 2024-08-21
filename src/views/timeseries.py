from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QContextMenuEvent, QColor
# ##################################################################
from src.models.timeseries import TimeseriesModel
from src.models.time_window import TimeWindowModel
from src.views.timeseries_header import TimeseriesHeaderView
from src.views.timeseries_graph import TimeseriesGraphView
# ##################################################################


class TimeseriesView(QWidget):
    COLOR = QColor("#346beb")

    def __init__(self, timeseries: TimeseriesModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._timeseries = timeseries
        self._time_window = time_window
        self.setLayout(QHBoxLayout())
        self._header = TimeseriesHeaderView(timeseries)
        self._header.setFixedWidth(100)
        self.layout().addWidget(self._header)
        self._graph  = TimeseriesGraphView(time_window, timeseries, self.COLOR)
        self._graph.setFixedHeight(50)
        self.layout().addWidget(self._graph)
        self.layout().setContentsMargins(0, 2, 2, 2)
        self._header.setFixedWidth(150)
