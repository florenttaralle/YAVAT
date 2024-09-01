from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QSlider
from PyQt6.QtGui import QColorConstants, QResizeEvent
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from src.models.video import VideoModel
from src.views.player_bar import PlayerBarView
from src.views.player_slider import PlayerSlider

class PlayerView(QWidget):
    def __init__(self, video: VideoModel|None=None, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._video: VideoModel|None = None
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
        self._slider = PlayerSlider()
        layout.addWidget(self._slider)
        self._bar = PlayerBarView()
        layout.addWidget(self._bar)
        self.set_video(video)

    def set_video(self, video: VideoModel|None):
        if self._video is not None:
            self._video.player.setVideoOutput(None)
            self._video.frame_id_changed.disconnect(self.onVideoFileFrameIdChanged)        
            self._video.ready_changed.disconnect(self.onVideoReadyChanged)
        self._video = video
        if self._video is not None:
            self._video_item.setVisible(True)
            self._first_frame = True
            self._video.player.setVideoOutput(self._video_item)
            self._video.frame_id_changed.connect(self.onVideoFileFrameIdChanged)
            self._video.ready_changed.connect(self.onVideoReadyChanged)
            self.onVideoReadyChanged(video.ready)
        else:
            self._video_item.setVisible(False)
            self.setEnabled(False)

    def onVideoReadyChanged(self, ready: bool):
        self.setEnabled(self._video.valid)
        if self._video.valid:
            self._slider.set_video(self._video)
            self._bar.set_video(self._video)
            self.onVideoFileFrameIdChanged(self._video.ready)

    def onVideoFileFrameIdChanged(self, frame_id: int):
        if self._first_frame:
            self.centerView()
            self._first_frame = True

    def resizeEvent(self, event: QResizeEvent):
        self.centerView()
        
    def centerView(self):
        self._gview.fitInView(self._video_item, Qt.AspectRatioMode.KeepAspectRatio)
        self._gview.centerOn(self._video_item)

