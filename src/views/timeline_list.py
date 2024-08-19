from PyQt6.QtWidgets import QWidget, QVBoxLayout
from src.models.timeline_list import TimelineListModel
from src.models.time_window import TimeWindowModel
from src.models.timeline_list_state import TimelineListState
from src.views.timeline_list_list import TimelineListListView
from src.views.timeline_list_bar import TimelineListBarView
from src.views.timeline_name import TimelineNameInputDialog
from src.views.event_properties import EventPropertiesDialog

class TimelineListView(QWidget):
    def __init__(self, timeline_list: TimelineListModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._timeline_list     = timeline_list
        self._time_window       = time_window
        self._state             = TimelineListState(timeline_list)
        self._name_dialog       = TimelineNameInputDialog(timeline_list)
        self._event_dialog      = EventPropertiesDialog()

        self.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)
        
        self._bar = TimelineListBarView(self._timeline_list, self._state, self._time_window)
        self._bar.edit_timeline_name.connect(self._name_dialog.exec)
        self._bar.edit_event.connect(self._event_dialog.exec)
        layout.addWidget(self._bar)
        
        self._list = TimelineListListView(self._timeline_list, self._state, self._time_window)
        self._list.setStyleSheet("border: 0px")
        self._list.edit_timeline_name.connect(self._name_dialog.exec)
        self._list.edit_event.connect(self._event_dialog.exec)
        layout.addWidget(self._list)
