from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from src.views.dialogs.annotation_editor import AnnotationEditorDialog

class TimelineEditorDialog(AnnotationEditorDialog):
    def _build_form(self, form: QFormLayout):
        self.setWindowTitle("Timeline Properties")
        AnnotationEditorDialog._build_form(self, form)
