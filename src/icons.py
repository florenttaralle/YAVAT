from enum import Enum
from PyQt6.QtGui import QIcon

# https://www.iconfinder.com/search/icons?family=unicons-line

class Icons(Enum):
    __ICON_FOLDER__ = "assets/icons/"
    Delete          = "delete.png"
    Range           = "range.png"
    Ponctual        = "ponctual.png"
    Mute            = "mute.png"
    Sound           = "sound.png"
    Play            = "play.png"
    Pause           = "pause.png"
    Forward         = "forward.png"
    ForwardStep     = "forward_step.png"
    BackwardStep    = "backward_step.png"
    Backward        = "backward.png"
    
    def icon(self) -> QIcon:
        return QIcon(self.__ICON_FOLDER__ + self.value)