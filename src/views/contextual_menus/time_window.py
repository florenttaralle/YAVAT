from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
# ##################################################################
from src.models.time_window import TimeWindowModel
from src.icons import Icons
# ##################################################################

class TimeWindowContextualMenu(QObject):
    def __init__(self, time_window: TimeWindowModel, frame_id: int, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._time_window   = time_window
        self._frame_id      = frame_id

        self._act_goto = QAction(Icons.Goto.icon(), "Goto here", self)
        self._act_goto.triggered.connect(self.onGoto)

    def attach(self, menu: QMenu):
        menu.addAction(self._act_goto)
        return self

    def onGoto(self):
        self._time_window.goto(self._frame_id)
