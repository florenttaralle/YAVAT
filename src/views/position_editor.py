from PyQt6.QtCore import QObject, Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QValidator
import re
from src.widgets.auto_pose_line_edit import AutoPauseLineEdit
from src.models.video_file import VideoFile, QTime

class TimeValidator(QValidator):
    # hh:mm:ss.zzz ; hh, mm & zzz are optional
    def __init__(self, maxValue: QTime, format: str="mm:ss:zzz", parent: QObject|None = None):
        QValidator.__init__(self, parent)
        self._maxValue = maxValue
        self._format = format

    def validate(self, input: str, pos: int) -> QValidator.State:
        state = QValidator.State.Intermediate
        value = QTime.fromString(input, self._format)
        if value.isValid():
            if QTime(0, 0, 0, 0) <= value < self._maxValue:
                state = QValidator.State.Acceptable
        return state, input, pos

class PositionEditor(AutoPauseLineEdit):
    def __init__(self, video_file: VideoFile, format: str="mm:ss.zzz", parent: QWidget|None = None):
        AutoPauseLineEdit.__init__(self, video_file.player, parent)
        self._video_file = video_file
        self._format = format
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip("Timestamp")
        self._video_file.ready_changed.connect(self.onVideoReadyChanged)
        self._video_file.position_changed.connect(self.onVideoFilePositionChanged)

    def onVideoReadyChanged(self, ready: bool):
        if self._video_file.valid:
            self.onVideoFilePositionChanged(self._video_file.position)
            validator = TimeValidator(self._video_file.duration, self._format)
            self.setValidator(validator)

    def onVideoFilePositionChanged(self, position: QTime):
        self.setText(position.toString(self._format))

    def focusOutEvent(self, event):
        value       = QTime.fromString(self.text(), self._format)
        frame_id    = round(self._video_file.to_frame_id(value))
        value       = self._video_file.to_position(frame_id)
        self.setText(value.toString(self._format))
        self._video_file.gotoPosition(value)
        AutoPauseLineEdit.focusOutEvent(self, event)
