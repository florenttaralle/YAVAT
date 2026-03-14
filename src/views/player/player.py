from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QColorConstants, QResizeEvent
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem

from src.models.video import VideoModel
from .player_bar import PlayerBarView
from .player_slider import PlayerSliderView

class PlayerView(QWidget):
    muted_changed = pyqtSignal(bool)
    "SIGNAL: muted_changed(muted: bool)"

    def __init__(self, video: VideoModel|None=None, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._video: VideoModel|None = None
        self._muted: bool = False
        self._first_frame   = True
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(500, 500)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)
        self._scene = QGraphicsScene()
        self._gview = QGraphicsView(self._scene)
        self._gview.setBackgroundBrush(QColorConstants.Black)
        self._gview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._gview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._video_item = QGraphicsVideoItem()
        self._scene.addItem(self._video_item)
        layout.addWidget(self._gview)
        self._gview.setStyleSheet("border: 0px")
        self._slider = PlayerSliderView()
        layout.addWidget(self._slider)
        self._bar = PlayerBarView()
        layout.addWidget(self._bar)
        self.set_video(video)

    @property
    def muted(self) -> bool:
        return self._muted

    def set_muted(self, muted: bool):
        muted = bool(muted)
        if muted != self._muted:
            self._muted = muted
            self.muted_changed.emit(self._muted)
        self._apply_mute_to_video()

    def set_video(self, video: VideoModel|None):
        if self._video is not None:
            try:
                self._video._audio_output.mutedChanged.disconnect(self.onVideoMutedChanged)
            except Exception:
                pass
        self._video_item.setVisible(False)
        self.setEnabled(False)
        self._video = video
        if self._video is not None:
            self._video.player.setVideoOutput(self._video_item)
            self._video.frame_id_changed.connect(self.onVideoFileFrameIdChanged)
            self._video.ready_changed.connect(self.onVideoReadyChanged)
            self.onVideoReadyChanged(video.ready)
        else:
            self._slider.set_video(None)
            self._bar.set_video(None)

    def onVideoReadyChanged(self, ready: bool):
        if self._video.valid:
            self._slider.set_video(self._video)
            self._bar.set_video(self._video)
            if self._video.player.hasAudio():
                self._video._audio_output.mutedChanged.connect(self.onVideoMutedChanged)
            self._apply_mute_to_video()
            self.onVideoFileFrameIdChanged(self._video.ready)
            self._video_item.setVisible(True)
            self._first_frame = True
            self.setEnabled(True)

    def onVideoMutedChanged(self, muted: bool):
        muted = bool(muted)
        if muted != self._muted:
            self._muted = muted
            self.muted_changed.emit(muted)

    def onVideoFileFrameIdChanged(self, frame_id: int):
        if self._first_frame:
            self.centerView()
            self._first_frame = True

    def resizeEvent(self, event: QResizeEvent):
        self.centerView()
        
    def centerView(self):
        self._gview.fitInView(self._video_item, Qt.AspectRatioMode.KeepAspectRatio)
        self._gview.centerOn(self._video_item)

    def _apply_mute_to_video(self):
        if self._video is None:
            return
        if not self._video.player.hasAudio():
            return
        if self._video._audio_output.isMuted() != self._muted:
            self._video._audio_output.setMuted(self._muted)
