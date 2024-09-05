from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from src.models.annotation import AnnotationModel
from src.icons import Icons
from src.views.contextual_menus.annotation import AnnotationContextualMenu, QMenu, QCursor

class AnnotationHeaderView(QWidget):
    def __init__(self, annotation: AnnotationModel, show_value: bool=False, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._annotation = annotation
        self.setLayout(QHBoxLayout())
        self.setContentsMargins(0, 0, 0, 0)

        self._btn_menu = QPushButton()
        self._btn_menu.setIcon(Icons.MenuV.icon())
        self._btn_menu.setIconSize(QSize(28, 28))
        self._btn_menu.setFlat(True)
        self._btn_menu.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._btn_menu.clicked.connect(self.onBtnMenu)
        self.layout().addWidget(self._btn_menu)

        widget = QWidget(self)
        self.layout().addWidget(widget)
        widget.setLayout(QVBoxLayout())
        widget.layout().setSpacing(5)
        widget.layout().setContentsMargins(0, 0, 0, 0)

        self._name_lbl = QLabel(annotation.name)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self._name_lbl.setFont(font)
        self._name_lbl.setWordWrap(True)
        widget.layout().addWidget(self._name_lbl)

        self._value_lbl = QLabel()
        self._value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        font = QFont()
        font.setPointSize(9)
        self._value_lbl.setFont(font)
        widget.layout().addWidget(self._value_lbl)
        self._value_lbl.setVisible(show_value)

        annotation.name_changed.connect(self._name_lbl.setText)

    def onBtnMenu(self):
        self._annotation.set_selected(True)
        menu = QMenu()
        ano_ctx_menu = AnnotationContextualMenu(self._annotation)
        ano_ctx_menu.attach(menu)
        menu.exec(QCursor.pos())
