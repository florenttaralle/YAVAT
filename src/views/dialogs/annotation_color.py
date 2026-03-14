from __future__ import annotations

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QColorDialog, QDialog, QHBoxLayout, QPushButton, QWidget

from src.icons import Icons
from src.models.annotation import AnnotationModel, AnnotationGroupModel


class AnnotationColorDialog(QColorDialog):
    def __init__(
        self,
        annotation: AnnotationModel,
        parent: QWidget | None = None,
        preferred_color: QColor | None = None,
    ):
        QColorDialog.__init__(self, annotation.color, parent)
        self.setWindowTitle("Annotation Color")
        self.setModal(True)
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        self.setOption(QColorDialog.ColorDialogOption.NoButtons, True)
        self.setCurrentColor(annotation.color)
        if preferred_color is not None and preferred_color.isValid():
            QColorDialog.setCustomColor(0, preferred_color)

        self._recursive = False

        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.addStretch(1)

        # build the 3 dialog buttons
        self._cancel_button = QPushButton("Cancel", self)
        self._apply_button = QPushButton("Apply", self)
        self._apply_recursive_button = QPushButton("Apply Recursive", self)
        # select button icons
        self._cancel_button.setIcon(Icons.Close.icon())
        self._apply_button.setIcon(Icons.MessageOk.icon())
        self._apply_recursive_button.setIcon(Icons.MessageOk.icon())
        # set the recursive button only visible for group annotations
        self._apply_recursive_button.setVisible(isinstance(annotation, AnnotationGroupModel))

        # Explicit order, independent from platform button conventions.
        self._buttons_layout.addWidget(self._cancel_button)
        self._buttons_layout.addWidget(self._apply_button)
        self._buttons_layout.addWidget(self._apply_recursive_button)

        self._cancel_button.clicked.connect(self.reject)
        self._apply_button.clicked.connect(self._on_apply_clicked)
        self._apply_recursive_button.clicked.connect(self._on_apply_recursive_clicked)

        layout = self.layout()
        if layout is not None:
            layout.addLayout(self._buttons_layout)

    @property
    def color(self) -> QColor:
        return self.currentColor()

    @property
    def recursive(self) -> bool:
        return self._recursive

    def _on_apply_clicked(self):
        self._recursive = False
        self.accept()

    def _on_apply_recursive_clicked(self):
        self._recursive = True
        self.accept()


def _apply_color_recursive(annotation: AnnotationModel, color: QColor):
    annotation.set_color(color)
    if isinstance(annotation, AnnotationGroupModel):
        for child in annotation:
            _apply_color_recursive(child, color)


def exec_annotation_color_dialog(
    annotation: AnnotationModel,
    parent: QWidget | None = None,
    preferred_color: QColor | None = None,
) -> bool:
    dialog = AnnotationColorDialog(annotation, parent, preferred_color=preferred_color)
    status = dialog.exec()
    if status != QDialog.DialogCode.Accepted:
        return False
    if dialog.recursive and isinstance(annotation, AnnotationGroupModel):
        _apply_color_recursive(annotation, dialog.color)
    else:
        annotation.set_color(dialog.color)
    return True
