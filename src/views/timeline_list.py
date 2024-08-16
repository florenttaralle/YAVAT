from PyQt6.QtWidgets import QWidget, QVBoxLayout
from src.models.timeline_list import TimeLineListModel
from src.models.time_window import TimeWindowModel
from src.views.timeline_list_list import TimeLineListListView
from src.views.timeline_list_bar import TimeLineListBarView

class TimeLineListView(QWidget):
    def __init__(self, timeline_list: TimeLineListModel, time_window: TimeWindowModel, fps: float, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._timeline_list     = timeline_list
        self._time_window       = time_window

        self.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)
        
        self._bar = TimeLineListBarView(timeline_list, time_window)
        layout.addWidget(self._bar)
        
        self._list = TimeLineListListView(timeline_list, time_window, fps)
        self._list.setStyleSheet("border: 0px")
        layout.addWidget(self._list)
