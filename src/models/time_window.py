from PyQt6.QtCore import QObject, pyqtSignal

class TimeWindowModel(QObject):
    MIN_SIZE    = 10
    ZOOM_STEP   = 1.1
    
    changed = pyqtSignal(int, int, int)
    
    def __init__(self, duration: int, position: int=0, parent: QObject|None = None):
        QObject.__init__(self, parent)
        self._center    = duration // 2
        self._size      = duration
        self._duration  = duration
        self._position  = position
        self._left      = None
        self._right     = None
        self._update_bounds()
        
    @property
    def left(self) -> int:
        return self._left

    @property
    def right(self) -> int:
        return self._right

    @property
    def position(self) -> int:
        return self._position
    @position.setter
    def posision(self, position: int):
        if position != self._position:
            self._position = position
            self._update_bounds()

    @property
    def duration(self) -> int:
        return self._duration
    
    def zoom_in(self):
        self._size = max(self.MIN_SIZE, int(self._size / self.ZOOM_STEP))
        self._update_bounds()

    def zoom_out(self):
        self._size = min(self._duration, int(self._size * self.ZOOM_STEP))
        self._update_bounds()
        
    def _update_bounds(self):
        self._left  = max(0, self._position - self._size // 2)
        self._right = min(self._duration - 1, self._left + self._size - 1)
        self.changed.emit(self._left, self._position, self._right)
    
    