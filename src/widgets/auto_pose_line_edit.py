from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLineEdit
from PyQt6.QtGui import QKeyEvent, QFocusEvent
from PyQt6.QtMultimedia import QMediaPlayer

class AutoPauseLineEdit(QLineEdit):
    """ 
        Automaticaly pauses player during edition.
        Reset value and loses focus on Escape Key
    """
    def __init__(self, player: QMediaPlayer|None=None, parent: QWidget|None=None):
        QLineEdit.__init__(self, parent)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._player:       QMediaPlayer|None = None
        self._was_playing:  bool = None
        self._prv_value:    str = None
        self.editingFinished.connect(self.clearFocus)
        self.set_player(player)

    def set_player(self, player: QMediaPlayer|None):
        self._player = player
        self.setEnabled(self._player is not None)

    def focusInEvent(self, event: QFocusEvent):
        QLineEdit.focusInEvent(self, event)
        self._was_playing   = self._player.isPlaying()
        self._prv_value     = self.text()
        self._player.pause()

    def focusOutEvent(self, event: QFocusEvent):
        QLineEdit.focusOutEvent(self, event)
        if self._was_playing:
            self._player.play()

    def keyPressEvent(self, event: QKeyEvent):
        QLineEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key.Key_Escape:
            self.setText(self._prv_value)
            self.clearFocus()
