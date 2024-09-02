from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from src.models.annotation import AnnotationModel
from src.icons import Icons
from src.views.contextual_menus.annotation import AnnotationContextualMenu, QMenu, QCursor

class AnnotationHeaderView(QWidget):
    def __init__(self, annotation: AnnotationModel, parent: QWidget|None = None):
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

        self._name_lbl = QLabel(annotation.name)
        self._name_lbl.font().setBold(True)
        self._name_lbl.setWordWrap(True)
        self.layout().addWidget(self._name_lbl)

        annotation.name_changed.connect(self._name_lbl.setText)

    def onBtnMenu(self):
        print("onBtnMenu 0")
        self._annotation.set_selected(True)
        menu = QMenu()
        ano_ctx_menu = AnnotationContextualMenu(self._annotation)
        ano_ctx_menu.attach(menu)
        menu.exec(QCursor.pos())
        print("onBtnMenu 1")
