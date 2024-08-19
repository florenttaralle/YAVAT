from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QDialog, QLabel, QLineEdit, QFormLayout, QDialogButtonBox, QPushButton
from src.models.event import EventModel

class EventPropertiesDialog(QDialog):
    def __init__(self, parent: QWidget|None=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Edit Event Properties")
        self.setModal(True)

        self._label_le = QLineEdit()
        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal)

        form = QFormLayout()
        form.addRow(QLabel("Label"), self._label_le)
        form.addRow(self._buttons)
        self.setLayout(form)

        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

    def exec(self, event: EventModel):
        self._label_le.setText(event.label)
        if QDialog.exec(self) == QDialog.DialogCode.Accepted:
            event.label = self._label_le.text()

