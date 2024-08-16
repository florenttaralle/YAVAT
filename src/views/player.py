from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QSlider
from PyQt6.QtGui import QColorConstants, QResizeEvent
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from src.models.video_file import VideoFile
from src.views.player_bar import PlayerBarView
from src.views.player_slider import PlayerSlider

class Player(QWidget):
    def __init__(self, video_file: VideoFile, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._video_file = video_file
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
        video_file.player.setVideoOutput(self._video_item)
        layout.addWidget(self._gview)
        self._gview.setStyleSheet("border: 0px")

        self._slider = PlayerSlider(video_file)
        layout.addWidget(self._slider)
        self._bar = PlayerBarView(video_file)
        layout.addWidget(self._bar)

        self._first_frame: bool = True
        self._video_file.frame_id_changed.connect(self.onVideoFileFrameIdChanged)

    def onVideoFileFrameIdChanged(self, frame_id: int):
        if self._first_frame:
            self.centerView()
            self._first_frame = True

    def resizeEvent(self, event: QResizeEvent):
        self.centerView()
        
    def centerView(self):
        self._gview.fitInView(self._video_item, Qt.AspectRatioMode.KeepAspectRatio)
        self._gview.centerOn(self._video_item)

