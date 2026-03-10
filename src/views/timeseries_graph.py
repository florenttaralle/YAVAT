from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPen, QColor
import pyqtgraph as pg
from src.models.timeseries import TimeseriesModel
from src.views.graph import GraphView, TimeWindowModel

class TimeseriesGraphView(GraphView):
    def __init__(self, time_window: TimeWindowModel, timeseries: TimeseriesModel, parent: QWidget|None=None):
        GraphView.__init__(self, time_window, parent)
        self._timeseries = timeseries

        # plot values
        self._curve = pg.PlotCurveItem()
        self._curve.setFillLevel(0)
        self._curve.setData(x=timeseries.X, y=timeseries.Y)
        self.addItem(self._curve)

        # initialize view
        self.onTimeseriesColorChanged(timeseries.color)
        self.setYRange(timeseries.ymin, timeseries.ymax)
        self._apply_time_window()

        # connect signals & slots
        self._timeseries.color_changed.connect(self.onTimeseriesColorChanged)
        self._timeseries.y_range_changed.connect(self.setYRange)

    def onTimeseriesColorChanged(self, color: QColor):
        pen = QPen(color)
        pen.setWidth(2)
        pen.setCosmetic(True)
        self._curve.setPen(pen)
        # update plot brush (area under curve)
        brush_color = QColor(color)
        brush_color.setAlphaF(.4)
        self._curve.setBrush(brush_color)
