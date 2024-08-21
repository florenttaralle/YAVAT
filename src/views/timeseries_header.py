from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.models.timeseries import TimeseriesModel

class TimeseriesHeaderView(QWidget):
    def __init__(self, timeseries: TimeseriesModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._timeseries = timeseries
        self.setLayout(QVBoxLayout())
        self._name_lbl = QLabel(timeseries.name)
        self._name_lbl.font().setBold(True)
        self._name_lbl.setWordWrap(True)
        self.layout().addWidget(self._name_lbl)
