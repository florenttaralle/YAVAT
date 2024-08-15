from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIntValidator
from src.widgets.auto_pose_line_edit import AutoPauseLineEdit
from src.models.video_file import VideoFile

class FrameIdEditor(AutoPauseLineEdit):
    def __init__(self, video_file: VideoFile, parent: QWidget|None = None):
        AutoPauseLineEdit.__init__(self, video_file.player, parent)
        self._video_file = video_file
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip("Frame Id")
        self._video_file.ready_changed.connect(self.onVideoReadyChanged)
        self._video_file.frame_id_changed.connect(self.onVideoFileFrameIdChanged)

    def onVideoReadyChanged(self, ready: bool):
        if self._video_file.valid:
            self.onVideoFileFrameIdChanged(self._video_file.frame_id)
            validator = QIntValidator(0, self._video_file.n_frames - 1)
            self.setValidator(validator)

    def onVideoFileFrameIdChanged(self, frame_id: int):
        self.setText(str(frame_id))
        
    def focusOutEvent(self, event):
        self._video_file.gotoFrameId(self._value())
        AutoPauseLineEdit.focusOutEvent(self, event)

    def _value(self) -> int:
        return int(self.text())        
        
