from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from src.models.annotation import AnnotationModel
from src.icons import Icons

class AnnotationHeaderView(QWidget):
    edit = pyqtSignal()
    "SIGNAL: edit()"

    def __init__(self, annotation: AnnotationModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._annotation = annotation
        self.setLayout(QHBoxLayout())
        self.setContentsMargins(0, 0, 0, 0)

        self._edit_btn = QPushButton()
        self._edit_btn.setIcon(Icons.Edit.icon())
        self._edit_btn.setIconSize(QSize(28, 28))
        self._edit_btn.setFlat(True)
        self._edit_btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self.layout().addWidget(self._edit_btn)

        self._name_lbl = QLabel(annotation.name)
        self._name_lbl.font().setBold(True)
        self._name_lbl.setWordWrap(True)
        self.layout().addWidget(self._name_lbl)

        annotation.name_changed.connect(self._name_lbl.setText)
        self._edit_btn.clicked.connect(self.edit)
