from PyQt6.QtWidgets import QWidget, QVBoxLayout
from src.models.timeline_list import TimelineListModel
from src.models.time_window import TimeWindowModel
from src.models.timeline_list_state import TimelineListState
from src.views.timeline_list_list import TimelineListListView
from src.views.timeline_list_bar import TimelineListBarView


class TimelineListView(QWidget):
    def __init__(self, timeline_list: TimelineListModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._timeline_list     = timeline_list
        self._time_window       = time_window
        self._state             = TimelineListState(timeline_list)

        self.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)
        
        self._bar = TimelineListBarView(self._timeline_list, self._state, self._time_window)
        layout.addWidget(self._bar)
        
        self._list = TimelineListListView(self._timeline_list, self._state, self._time_window)
        self._list.setStyleSheet("border: 0px")
        layout.addWidget(self._list)
