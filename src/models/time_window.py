from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.video_file import VideoFile

class TimeWindowModel(QObject):
    window_changed      = pyqtSignal(int, int, int) 
    "SIGNAL: window_changed(left: int, position: int, right: int)"
    size_changed        = pyqtSignal(int)
    "SIGNAL: size_changed(size: int)"
    left_changed        = pyqtSignal(int)
    "SIGNAL: left_changed(left: int)"
    position_changed    = pyqtSignal(int)
    "SIGNAL: position_changed(position: int)"
    right_changed       = pyqtSignal(int)
    "SIGNAL: right_changed(right: int)"
    playing_changed     = pyqtSignal(bool)
    "SIGNAL: playing_changed(playing: bool)"
    
    def __init__(self, duration: int, position: int=0, playing: bool=False, 
                 zoom_step: float=1.1, min_size: int=10, parent: QObject|None = None):
        QObject.__init__(self, parent)
        self._center    = duration // 2
        self._size      = duration
        self._duration  = duration
        self._position  = position
        self._left      = None
        self._right     = None
        self._update_bounds()
        self._playing   = playing
        self._zoom_step = zoom_step
        self._min_size  = min_size
        
    @classmethod
    def from_video_file(cls, video_file: VideoFile, **kwargs) -> TimeWindowModel:
        time_window = cls(video_file.n_frames, video_file.frame_id, video_file.playing, **kwargs)
        video_file.playing_changed.connect(lambda playing: TimeWindowModel.playing.__set__(time_window, playing))
        video_file.frame_id_changed.connect(time_window.goto)
        time_window.position_changed.connect(video_file.gotoFrameId)
        return time_window
    
    @property
    def left(self) -> int:
        return self._left
    def _set_left(self, left: int) -> bool:
        if left != self._left:
            self._left = left
            self.left_changed.emit(left)
            return True
        return False

    @property
    def right(self) -> int:
        return self._right
    def _set_right(self, right: int) -> bool:
        if right != self._right:
            self._right = right
            self.right_changed.emit(right)
            return True
        return False

    @property
    def position(self) -> int:
        return self._position
    @position.setter
    def position(self, position: int):
        self.goto(position)

    def goto(self, position: int):
        position = max(position, 0)
        position = min(position, self._duration - 1)
        if position != self._position:
            self._position = position
            self._update_bounds()
            self.position_changed.emit(position)
            self.window_changed.emit(self._left, self._position, self._right)
    
    @property
    def size(self) -> int:
        return self._size
    @size.setter
    def size(self, size: int):
        if size != self._size:
            self._size = size
            self.size_changed.emit(self._size)
            if self._update_bounds():
                self.window_changed.emit(self._left, self._position, self._right)

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def playing(self) -> bool:
        return self._playing
    @playing.setter
    def playing(self, playing: bool):
        if playing != self._playing:
            self._playing = playing
            self.playing_changed.emit(playing)
    
    def zoom_in(self):
        self.size = max(self._min_size, int(self._size / self._zoom_step))

    def zoom_out(self):
        self.size = min(self._duration, int(self._size * self._zoom_step))
        
    def reset(self):
        self.size = self._duration

    def _update_bounds(self) -> bool:
        changed = False
        if self._position <= (self._size // 2):
            changed |= self._set_left(0)
            changed |= self._set_right(self._size - 1)
        elif self._position >= (self._duration - 1 - self._size // 2):
            changed |= self._set_left(self._duration - self._size)
            changed |= self._set_right(self._duration - 1)
        else:
            changed |= self._set_left(self._position - self._size // 2)
            changed |= self._set_right(self._left + self._size - 1)
        return changed
