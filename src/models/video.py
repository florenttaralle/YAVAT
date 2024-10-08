from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QTime
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudioDevice, QMediaDevices
from src.video_stream_info import VideoStreamInfo
from src.models.time_window import TimeWindowModel
import os

class VideoModel(QObject):
    ready_changed       = pyqtSignal(bool)
    "SIGNAL: ready_changed(ready: bool)"
    error_changed       = pyqtSignal(str)
    "SIGNAL: error_changed(error: str)"
    frame_id_changed    = pyqtSignal(int)
    "SIGNAL: frame_id_changed(frame_id: int)"
    position_changed    = pyqtSignal(QTime)
    "SIGNAL: position_changed(position: QTime)"
    playing_changed     = pyqtSignal(bool)
    "SIGNAL: playing_changed(playing: bool)"
    
    def __init__(self, video_path: str, parent: QObject|None = None):
        QObject.__init__(self, parent)
        self._video_path    = video_path
        self._time_window:  TimeWindowModel|None = None
        self._error:        str = ""
        self._ready:        bool = False
        self._stream_info:  VideoStreamInfo | None = None
        self._player        = QMediaPlayer()
        self._audio_device  = QAudioDevice(QMediaDevices.defaultAudioOutput())
        self._audio_output  = QAudioOutput(self._audio_device)
        self._player.setAudioOutput(self._audio_output)
        self._player.mediaStatusChanged.connect(self.onPlayerMediaStatusChanged)
        self._player.positionChanged.connect(self.onPlayerPositionChanged)
        self._player.playbackStateChanged.connect(self.onPlayerPlaybackStateChanged)

        # load video stream info (so it is always available)
        try:
            self._stream_info = VideoStreamInfo.load(self._video_path)
        except Exception as what:
            self._set_error(f"Reading Video Stream Info: {what}")
            self._set_ready(True)
        else:
            self._player.setSource(QUrl.fromLocalFile(video_path))

    def data(self):
        return {
            "video_filename":   os.path.basename(self._video_path),
            "duration_ms":      self.duration.msecsSinceStartOfDay(),
            "duration_frames":  self.n_frames,
            "fps":              self.fps,
            "width":            self._stream_info.width,
            "height":           self._stream_info.height,            
        }

    @property
    def time_window(self) -> TimeWindowModel|None:
        return self._time_window

    @property
    def player(self) -> QMediaPlayer:
        return self._player

    @property
    def path(self) -> str:
        return self._video_path

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
    @frame_id.setter
    def frame_id(self, frame_id: int):
        self.gotoFrameId(frame_id)

    @property
    def position(self) -> QTime:
        return QTime.fromMSecsSinceStartOfDay(self._player.position())
    @position.setter
    def position(self, position: QTime):
        self.gotoPosition(position)

    @property
    def n_frames(self) -> int:
        return self.to_frame_id(self.duration)

    @property
    def duration(self) -> QTime:
        return QTime.fromMSecsSinceStartOfDay(round(self._stream_info.duration_s * 1000))

    @property
    def playing(self) -> bool:
        return self._player.isPlaying()

    def gotoFrameId(self, frame_id: int):
        if frame_id != self.frame_id:
            self.gotoPosition(self.to_position(frame_id))
    
    def gotoPosition(self, position: QTime):
        if position != self.position:
            self._player.setPosition(position.msecsSinceStartOfDay())

    def _set_time_window(self, time_window: TimeWindowModel):
        self._time_window = time_window
        self._time_window.position_changed.connect(self.gotoFrameId)
        self.frame_id_changed.connect(self._time_window.set_position)
        self.playing_changed.connect(self._time_window.set_playing)

    def onPlayerMediaStatusChanged(self, status: QMediaPlayer.MediaStatus):
        match status:
            case QMediaPlayer.MediaStatus.LoadingMedia:
                self._set_error("")
                self._set_ready(False)
            case QMediaPlayer.MediaStatus.InvalidMedia:
                self._error = self._player.errorString()
                self._set_ready(True)
            case QMediaPlayer.MediaStatus.LoadedMedia:
                time_window = TimeWindowModel(self.n_frames, self.frame_id, self.playing)
                self._set_time_window(time_window)
                self._set_ready(True)
    
    def onPlayerPlaybackStateChanged(self, state: QMediaPlayer.PlaybackState):
        playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        self.playing_changed.emit(playing)

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
