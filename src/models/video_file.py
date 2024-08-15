from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QTime
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudioDevice, QMediaDevices
from src.video_stream_info import VideoStreamInfo

class VideoFile(QObject):
    ready_changed       = pyqtSignal(bool)
    error_changed       = pyqtSignal(str)
    frame_id_changed    = pyqtSignal(int)
    position_changed    = pyqtSignal(QTime)
    
    def __init__(self, path: str, parent: QObject|None = None):
        QObject.__init__(self, parent)
        self._path          = path
        self._error:        str = ""
        self._ready:        bool = False
        self._stream_info:  VideoStreamInfo | None = None
        self._player        = QMediaPlayer()
        self._audio_device = QAudioDevice(QMediaDevices.defaultAudioOutput())
        self._audio_output = QAudioOutput(self._audio_device)
        self._player.setAudioOutput(self._audio_output)
        self._player.mediaStatusChanged.connect(self.onPlayerMediaStatusChanged)
        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.positionChanged.connect(self.onPlayerPositionChanged)

    @property
    def player(self) -> QMediaPlayer:
        return self._player

    @property
    def path(self) -> str:
        return self._path

    @property
    def ready(self) -> str:
        return self._ready
    def _set_ready(self, ready: bool):
        if ready != self._ready:
            self._ready = ready
            self.ready_changed.emit(ready)

    @property
    def error(self) -> str:
        return self._error
    def _set_error(self, error: str):
        if error != self._error:
            self._error = error
            self.error_changed.emit(error)

    @property
    def valid(self) -> bool:
        return self._ready and not self._error
    
    def to_frame_id(self, position: QTime) -> int:
        position_s = position.msecsSinceStartOfDay() / 1000
        return round(self._stream_info.fps * position_s)

    def to_position(self, frame_id: int) -> QTime:
        position_ms = round(1000 * frame_id / self._stream_info.fps)
        return QTime.fromMSecsSinceStartOfDay(position_ms)
    
    @property
    def fps(self) -> float:
        return self._stream_info.fps
    
    @property
    def frame_id(self) -> int:
        return self.to_frame_id(self.position)
    
    @property
    def position(self) -> QTime:
        return QTime.fromMSecsSinceStartOfDay(self._player.position())

    @property
    def n_frames(self) -> int:
        return self.to_frame_id(self.duration)

    @property
    def duration(self) -> QTime:
        return QTime.fromMSecsSinceStartOfDay(round(self._stream_info.duration_s * 1000))

    def gotoFrameId(self, frame_id: int):
        self.gotoPosition(self.to_position(frame_id))
    
    def gotoPosition(self, position: QTime):
        self._player.setPosition(position.msecsSinceStartOfDay())

    def onPlayerMediaStatusChanged(self, status: QMediaPlayer.MediaStatus):
        match status:
            case QMediaPlayer.MediaStatus.LoadingMedia:
                self._set_error("")
                self._stream_info = None
                self._set_ready(False)
            case QMediaPlayer.MediaStatus.InvalidMedia:
                self._error = self._player.errorString()
                self._set_ready(True)
            case QMediaPlayer.MediaStatus.LoadedMedia:
                try:
                    self._stream_info = VideoStreamInfo.load(self._path)
                    self._set_error("")
                except Exception as what:
                    self._set_error(f"Reading Video Stream Info: {what}")
                self._set_ready(True)

    def onPlayerPositionChanged(self, position_ms: int):
        # automaticaly pause video on last frame (avoid stop or stale state)
        if self._player.position() == self._player.duration():
            self._player.pause()
        position = QTime.fromMSecsSinceStartOfDay(position_ms)
        self.position_changed.emit(position)
        self.frame_id_changed.emit(self.to_frame_id(position))

    def play(self):
        assert self.valid
        if self._player.position() == self._player.duration():
            self._player.setPosition(0)
        self._player.play()
    
    def pause(self):
        assert self.valid
        self._player.pause()
