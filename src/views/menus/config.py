from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QKeySequence, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QMenu, QStyle, QWidget

from src.icons import Icons

class ConfigMenu(QMenu):
    on_text_bigger = pyqtSignal()
    on_text_smaller = pyqtSignal()
    on_graph_height = pyqtSignal()
    on_auto_play = pyqtSignal(bool)
    on_default_color = pyqtSignal()
    
    def __init__(self, parent: QWidget|None=None):
        QMenu.__init__(self, "&Config", parent)

        self._act_text_bigger = self.addAction(Icons.ZoomIn.icon(), "Bigger texts")
        self._act_text_bigger.setShortcut(QKeySequence("Ctrl+Shift+="))
        self._act_text_bigger.triggered.connect(self.on_text_bigger)

        self._act_text_smaller = self.addAction(Icons.ZoomOut.icon(), "Smaller texts")
        self._act_text_smaller.setShortcut(QKeySequence("Ctrl+Shift+-"))
        self._act_text_smaller.triggered.connect(self.on_text_smaller)

        self._act_graph_height = self.addAction("Graphs min height")
        self._act_graph_height.triggered.connect(self.on_graph_height)

        self._act_auto_play = self.addAction("Auto play on load")
        self._act_auto_play.setCheckable(True)
        self._act_auto_play.triggered.connect(self.on_auto_play)

        self._act_default_color = self.addAction("Default annotation color")
        self._act_default_color.triggered.connect(self.on_default_color)
        # Keep the current color in state so we can re-render the icon whenever
        # app style metrics change (icon size is style-driven, not hardcoded).
        self._default_color = QColor("#346beb")
        self._refresh_default_color_icon()

    def set_auto_play(self, auto_play: bool):
        self._act_auto_play.setChecked(bool(auto_play))

    def set_default_color(self, color: QColor):
        if color is None or not color.isValid():
            return
        self._default_color = QColor(color)
        self._refresh_default_color_icon()

    def _refresh_default_color_icon(self):
        # Ask Qt style for the small-icon size used in menus.
        # In YavatView, this value is controlled globally through a proxy style.
        icon_side = self.style().pixelMetric(QStyle.PixelMetric.PM_SmallIconSize, None, self)
        icon_side = max(8, int(icon_side))
        pixmap = QPixmap(icon_side, icon_side)
        pixmap.fill(self._default_color)
        # Add a border so very light colors stay visible against bright themes.
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawRect(0, 0, icon_side - 1, icon_side - 1)
        painter.end()
        self._act_default_color.setIcon(QIcon(pixmap))

    def changeEvent(self, event):
        QMenu.changeEvent(self, event)
        # Rebuild the color square when font/style changes, because style metric
        # driven icon size may have changed.
        if event.type() in (QEvent.Type.StyleChange, QEvent.Type.FontChange):
            self._refresh_default_color_icon()
