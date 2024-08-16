from enum import Enum
from PyQt6.QtGui import QIcon

# https://www.iconfinder.com/search/icons?family=unicons-line

class Icons(Enum):
    __ICON_FOLDER__ = "assets/icons/"
    Yavat           = "yavat.png"
    Delete          = "delete.png"
    Range           = "range.png"
    Ponctual        = "ponctual.png"
    AddRange        = "range_add.png"
    AddPonctual     = "ponctual_add.png"
    Mute            = "mute.png"
    Sound           = "sound.png"
    Play            = "play.png"
    Pause           = "pause.png"
    Forward         = "forward.png"
    ForwardStep     = "forward_step.png"
    BackwardStep    = "backward_step.png"
    Backward        = "backward.png"
    Timeline        = "timeline.png"
    
    def icon(self) -> QIcon:
        return QIcon(self.__ICON_FOLDER__ + self.value)
