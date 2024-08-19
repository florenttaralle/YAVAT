from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.models.timeline import TimelineModel

class TimelineHeaderView(QWidget):
    def __init__(self, timeline: TimelineModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._timeline = timeline
        self.setLayout(QVBoxLayout())
        self._name_lbl = QLabel(timeline.name)
        self._name_lbl.font().setBold(True)
        self._name_lbl.setWordWrap(True)
        self.layout().addWidget(self._name_lbl)
        timeline.name_changed.connect(self._name_lbl.setText)

