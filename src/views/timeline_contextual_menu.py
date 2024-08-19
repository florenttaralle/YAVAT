from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenu, QWidget
from PyQt6.QtGui import QCursor
# ##################################################################
from src.models.timeline import TimelineModel, EventModel
from src.models.time_window import TimeWindowModel
from src.icons import Icons
# ##################################################################

class TimelineContextualMenu(QMenu):
    def __init__(self, timeline: TimelineModel, time_window: TimeWindowModel, parent: QWidget|None=None):
        QMenu.__init__(self, parent)
        self._timeline      = timeline
        self._time_window   = time_window
        self._frame_id:     int = None
        self._event:        EventModel|None = None
    
        self._act_goto = self.addAction(Icons.Goto.icon(), "&Goto here")
        self._act_goto.triggered.connect(self.onGoto)
        self.addSeparator()

        self._act_add = self.addAction(Icons.EventAdd.icon(), "&Add Event starting here")
        self._act_add.triggered.connect(self.onCreateEvent)

        self._act_edit = self.addAction(Icons.EventInfo.icon(), "&Edit Event")
        self._act_edit.triggered.connect(self.onEditEvent)

        self._act_rem = self.addAction(Icons.EventRem.icon(), "&Delete Event")
        self._act_rem.triggered.connect(self.onDeleteEvent)

    def show(self, frame_id: int):
        self._frame_id = frame_id
        self._event = self._timeline.at_frame_id(frame_id)
        self._act_add.setEnabled(self._event is None)
        self._act_edit.setEnabled(self._event is not None)
        self._act_rem.setEnabled(self._event is not None)
        self.exec(QCursor.pos())
    
    def onGoto(self):
        self._time_window.goto(self._frame_id)
    
    def onCreateEvent(self):
        self._timeline.add(self._frame_id, self._frame_id)

    def onDeleteEvent(self):
        self._timeline.rem(self._event)
    
    def onEditEvent(self):
        print(f"On Edit Event {self._event}")
