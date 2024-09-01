from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from src.models.annotation import AnnotationModel

class AnnotationEditorDialog(QDialog):
    def __init__(self, parent: QWidget|None=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Annotation Properties")
        self.setModal(True)

        form = QFormLayout()
        form.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.setLayout(form)

        self._build_form(form)
        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        form.addRow(self._buttons)

    def _build_form(self, form: QFormLayout):
        self._name_le = QLineEdit()
        form.addRow(QLabel("Name"), self._name_le)

        self._color = None
        self._color_btn = QPushButton()
        self._color_btn.setAutoFillBackground(True)
        self._color_btn.setFlat(True)
        self._color_btn.clicked.connect(self.colorBtnClicked)
        form.addRow(QLabel("Color"), self._color_btn)
        
    def from_annotation(self, annotation: AnnotationModel):
        self._name_le.setText(annotation.name)
        self._set_color(annotation.color)

    def _set_color(self, color: QColor):
        self._color = color
        self._color_btn.setPalette(QPalette(color))

    def colorBtnClicked(self):
        color = QColorDialog.getColor(self._color)
        if color.isValid():
            self._set_color(color)
    
    def to_annotation(self, annotation: AnnotationModel):
        annotation.set_name(self._name_le.text())
        annotation.set_color(self._color)
    
    def exec(self, annotation: AnnotationModel) -> bool:
        self.from_annotation(annotation)
        status = QDialog.exec(self)
        if status == QDialog.DialogCode.Accepted:
            self.to_annotation(annotation)
            return True
        else:
            return False
