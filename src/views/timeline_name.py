from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QDialog, QLabel, QLineEdit, QFormLayout, QDialogButtonBox, QPushButton
from src.models.timeline_list import TimelineListModel, TimelineModel

class TimelineNameInputDialog(QDialog):
    def __init__(self, timeline_list: TimelineListModel, parent: QWidget|None=None):
        QDialog.__init__(self, parent)
        self._timeline_list     = timeline_list
        self._crt_timeline:     TimelineModel = None
        self.setWindowTitle("Edit Timeline Name")
        self.setModal(True)

        self._line_edit = QLineEdit()        
        self._error_lbl = QLabel()
        self._error_lbl.setStyleSheet("QLabel { color : red; }")

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal)

        form = QFormLayout()
        form.addRow(QLabel("Enter a non-empty unique name for this Timeline."))
        form.addRow(self._line_edit)
        form.addRow(self._error_lbl)
        form.addRow(self._buttons)
        self.setLayout(form)

        self._line_edit.textChanged.connect(self.onTextChanged)
        self._buttons.accepted.connect(self.onOkButton)
        self._buttons.rejected.connect(self.onCancelButton)

    def exec(self, timeline: TimelineModel) -> int:
        self._crt_timeline = timeline 
        self._line_edit.setText(timeline.name)
        return QDialog.exec(self)
    
    def _validate(self, name: str) -> bool:
        if name == "":
            self._error_lbl.setText("Name cannot be empty.")
            return False
        if (name != self._crt_timeline.name) and (name in self._timeline_list.names()):
            self._error_lbl.setText("Name already taken.")
            return False        
        return True

    @property
    def ok_button(self) -> QPushButton:
        return self._buttons.button(QDialogButtonBox.StandardButton.Ok)

    def onTextChanged(self, text: str):
        valid = self._validate(text)
        self.ok_button.setEnabled(valid)

    def onOkButton(self):
        self._crt_timeline.name = self._line_edit.text()
        self.accept()
    
    def onCancelButton(self):
        self.reject()
