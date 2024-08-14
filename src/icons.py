from enum import Enum
from PyQt6.QtGui import QIcon

# https://www.iconfinder.com/search/icons?family=glyph-23

class Icons(Enum):
    __ICON_FOLDER__ = "assets/icons/"
    Add     = "add.png"
    Delete  = "delete.png"
    Swap    = "swap.png"

    def icon(self) -> QIcon:
        return QIcon(self.__ICON_FOLDER__ + self.value)