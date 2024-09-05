from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from src.icons import Icons


class ColorButton(QWidget):
    def __init__(self, delete_button: bool=True):
        QWidget.__init__(self)
        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)        
        self._color: QColor|None = None

        self._color_btn = QPushButton()
        self._color_btn.clicked.connect(self.onColorBtn)
        self._color_btn.setFlat(True)
        self._color_btn.setAutoFillBackground(True)
        self.layout().addWidget(self._color_btn)
        
        self._delete_btn = QPushButton()
        self._delete_btn.setFixedWidth(30)
        self._delete_btn.setIcon(Icons.ColorDelete.icon())
        self._delete_btn.clicked.connect(self.onDeleteBtn)
        self.layout().addWidget(self._delete_btn)
        self._delete_btn.setVisible(delete_button)

    @property
    def color(self) -> QColor|None:
        return self._color if self._color.isValid() else None

    def set_color(self, color: QColor|None):
        self._color = color if color is not None else QColor()
        self._color_btn.setPalette(QPalette(self._color))
        
    def onColorBtn(self):
        color = QColorDialog.getColor(self._color)
        if color.isValid():
            self.set_color(color)

    def onDeleteBtn(self):
        self.set_color(None)
    