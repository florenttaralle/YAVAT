from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIntValidator
from src.widgets.auto_pose_line_edit import AutoPauseLineEdit
from src.models.video import VideoModel

class FrameIdEditor(AutoPauseLineEdit):
    def __init__(self, video: VideoModel|None=None, parent: QWidget|None = None):
        AutoPauseLineEdit.__init__(self, None, parent)
        self._video: VideoModel|None = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip("Frame Id")
        self.set_video(video)

    def set_video(self, video: VideoModel|None):
        self._video = video
        if self._video is not None:
            self._video.ready_changed.connect(self.onVideoReadyChanged)
            self._video.frame_id_changed.connect(self.onVideoFileFrameIdChanged)
            self.onVideoFileFrameIdChanged(self._video.frame_id)
            AutoPauseLineEdit.set_player(self, self._video.player)
        else:
            self.setText("")
            AutoPauseLineEdit.set_player(self, None)


    def onVideoReadyChanged(self, ready: bool):
        if self._video.valid:
            self.onVideoFileFrameIdChanged(self._video.frame_id)
            validator = QIntValidator(0, self._video.n_frames - 1)
            self.setValidator(validator)

    def onVideoFileFrameIdChanged(self, frame_id: int):
        self.setText(str(frame_id))
        
    def focusOutEvent(self, event):
        self._video.gotoFrameId(self._value())
        AutoPauseLineEdit.focusOutEvent(self, event)

    def _value(self) -> int:
        return int(self.text())        
        
