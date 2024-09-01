from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from src.models.timeline import TimelineModel, EventModel

class EventEditorDialog(QDialog):
    def __init__(self, parent: QWidget|None=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Event Properties")
        self.setModal(True)

        form = QFormLayout()
        self.setLayout(form)
        
        self._build_form(form)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        form.addRow(self._buttons)

    def _build_form(self, form: QFormLayout):
        self._timeline_cb = QComboBox()
        self._timeline_cb.setEditable(False)
        form.addRow(QLabel("Timeline"), self._timeline_cb)

        self._first_lbl = QLabel()
        form.addRow(QLabel("First"), self._first_lbl)
        
        self._last_lbl = QLabel()
        form.addRow(QLabel("Last"), self._last_lbl)

        self._label_le = QLineEdit()
        form.addRow(QLabel("Label"), self._label_le)


    def from_event(self, event: EventModel):
        timeline:   TimelineModel = event.parent()
        timelines   = [annotation for annotation in timeline.parent() if isinstance(annotation, TimelineModel)]
        timelines   = [tl for tl in timelines if (tl == timeline) or (tl.can_add(event.first, event.last))]
        
        self._timeline_cb.clear()
        for timeline_ in timelines:
            self._timeline_cb.addItem(timeline_.name, timeline_)
        index = self._timeline_cb.findData(timeline)
        self._timeline_cb.setCurrentIndex(index)        
        
        self._first_lbl.setText(str(event.first))
        self._last_lbl.setText(str(event.last))
        self._label_le.setText(event.label)

    def to_event(self, event: EventModel):
        # update label
        event.set_label(self._label_le.text())
        # if required, change the event from one timeline to another
        new_timeline: TimelineModel = self._timeline_cb.currentData()
        event.move_to(new_timeline)

    def exec(self, event: EventModel) -> bool:
        self.from_event(event)
        status = QDialog.exec(self)
        if status == QDialog.DialogCode.Accepted:
            self.to_event(event)
            return True
        else:
            return False
