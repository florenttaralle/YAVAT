from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QMenu, QWidget

from src.icons import Icons

class FileMenu(QMenu):
    on_load = pyqtSignal()
    on_quit = pyqtSignal()
    on_save = pyqtSignal()
        
    def __init__(self, parent: QWidget|None=None):
        QMenu.__init__(self, "&File", parent)

        self._act_load = self.addAction(Icons.Load.icon(), "Load")
        self._act_load.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_O))
        self._act_load.triggered.connect(self.on_load)

        self._act_save = self.addAction(Icons.Save.icon(), "Save")
        self._act_save.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S))
        self._act_save.triggered.connect(self.on_save)

        self.addSeparator()

        self._act_quit = self.addAction(Icons.Quit.icon(), "Quit")
        self._act_quit.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Q))
        self._act_quit.triggered.connect(self.on_quit)

    def set_can_save(self, can_save: bool):
        self._act_save.setEnabled(can_save)
