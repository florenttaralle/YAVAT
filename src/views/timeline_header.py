from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.models.timeline import TimelineModel

class QLabelWithDblClick(QLabel):
    double_click = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.double_click.emit()

class TimelineHeaderView(QWidget):
    edit_timeline_name = pyqtSignal(TimelineModel)
    "SIGNAL: edit_timeline_name(timeline: TimelineModel)"

    def __init__(self, timeline: TimelineModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._timeline = timeline
        self.setLayout(QVBoxLayout())
        self._name_lbl = QLabelWithDblClick(timeline.name)
        self._name_lbl.font().setBold(True)
        self._name_lbl.setWordWrap(True)
        self._name_lbl.double_click.connect(self.onNameLableDoubleClick)
        self.layout().addWidget(self._name_lbl)
        timeline.name_changed.connect(self._name_lbl.setText)

    def onNameLableDoubleClick(self):
        self.edit_timeline_name.emit(self._timeline)
        