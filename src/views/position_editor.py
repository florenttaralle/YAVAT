from PyQt6.QtCore import QObject, Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QValidator
import re
from src.widgets.auto_pose_line_edit import AutoPauseLineEdit
from src.models.video import VideoModel, QTime

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
    def __init__(self, video: VideoModel|None=None, format: str="mm:ss.zzz", parent: QWidget|None = None):
        AutoPauseLineEdit.__init__(self, None, parent)
        self._video: VideoModel|None = None
        self._format = format
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip("Timestamp")

    def set_video(self, video: VideoModel|None):
        if self._video is not None:
            self._video.ready_changed.disconnect(self.onVideoReadyChanged)
            self._video.position_changed.disconnect(self.onVideoFilePositionChanged)
        self._video = video
        if self._video is not None:
            self._video.ready_changed.connect(self.onVideoReadyChanged)
            self._video.position_changed.connect(self.onVideoFilePositionChanged)
            self.onVideoFilePositionChanged(self._video.position)
            AutoPauseLineEdit.set_player(self, self._video.player)
        else:
            self.setText("")
            AutoPauseLineEdit.set_player(self, None)


    def onVideoReadyChanged(self, ready: bool):
        if self._video.valid:
            self.onVideoFilePositionChanged(self._video.position)
            validator = TimeValidator(self._video.duration, self._format)
            self.setValidator(validator)

    def onVideoFilePositionChanged(self, position: QTime):
        self.setText(position.toString(self._format))

    def focusOutEvent(self, event):
        value       = QTime.fromString(self.text(), self._format)
        frame_id    = round(self._video.to_frame_id(value))
        value       = self._video.to_position(frame_id)
        self.setText(value.toString(self._format))
        self._video.gotoPosition(value)
        AutoPauseLineEdit.focusOutEvent(self, event)
