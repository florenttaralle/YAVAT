from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
# ##################################################################
from src.models.timeline import TimelineModel, EventModel
from src.models.time_window import TimeWindowModel
from src.views.dialogs.event_editor import EventEditorDialog
from src.icons import Icons
# ##################################################################

class TimelineContextualMenu(QObject):
    def __init__(self, time_window: TimeWindowModel, timeline: TimelineModel, frame_id: int, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._time_window   = time_window
        self._timeline      = timeline
        self._frame_id      = frame_id
        self._event         = timeline.at_frame_id(frame_id)
    
        self._act_add = QAction(Icons.EventAdd.icon(), "Add Event here", self)
        self._act_add.triggered.connect(self.onCreateEvent)
        self._act_add.setEnabled(self._event is None)

        self._act_edit = QAction(Icons.EventInfo.icon(), "Edit Event", self)
        self._act_edit.triggered.connect(self.onEditEvent)
        self._act_edit.setEnabled(self._event is not None)

        self._act_rem = QAction(Icons.EventRem.icon(), "Delete Event", self)
        self._act_rem.triggered.connect(self.onDeleteEvent)
        self._act_edit.setEnabled(self._event is not None)        

    def attach(self, menu: QMenu):
        menu.addAction(self._act_add)
        menu.addAction(self._act_edit)
        menu.addAction(self._act_rem)
        return self
    
    def onCreateEvent(self):
        self._timeline.add(EventModel(self._frame_id, self._frame_id))

    def onDeleteEvent(self):
        self._timeline.remove(self._event)
    
    def onEditEvent(self):
        if EventEditorDialog().exec(self._event):
            self._time_window.goto(self._frame_id)
