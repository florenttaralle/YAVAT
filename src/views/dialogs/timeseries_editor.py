from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from src.views.dialogs.annotation_editor import AnnotationEditorDialog
from src.models.timeseries import TimeseriesModel

class TimeseriesEditorDialog(AnnotationEditorDialog):
    FLOAT_RE = QRegularExpression("[-+]?\d+(?:\.\d{1,2})?")
    
    def _build_form(self, form: QFormLayout):
        self.setWindowTitle("Timeseries Properties")
        AnnotationEditorDialog._build_form(self, form)

    def _build_form(self, form: QFormLayout):
        AnnotationEditorDialog._build_form(self, form)
        self._ymin_le           = QLineEdit()
        self._ymin_validator    = QRegularExpressionValidator(self.FLOAT_RE)
        self._ymin_le.setValidator(self._ymin_validator)
        form.addRow(QLabel("YMin"), self._ymin_le)
        self._ymax_le = QLineEdit()
        self._ymax_validator    = QRegularExpressionValidator(self.FLOAT_RE)
        self._ymax_le.setValidator(self._ymax_validator)
        form.addRow(QLabel("YMax"), self._ymax_le)

    def from_annotation(self, annotation: TimeseriesModel):
        AnnotationEditorDialog.from_annotation(self, annotation)
        self._ymin_le.setText(str(round(annotation.ymin, 2)))
        self._ymax_le.setText(str(round(annotation.ymax, 2)))

    def to_annotation(self, annotation: TimeseriesModel):
        AnnotationEditorDialog.to_annotation(self, annotation)
        annotation.set_y_range(
            float(self._ymin_le.text()), 
            float(self._ymax_le.text())
        )
    
    
