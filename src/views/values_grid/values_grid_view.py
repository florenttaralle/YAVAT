from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from .values_grid_model import ValueGridModel, AnnotationListModel, TimeWindowModel

class ValuesGridView(QTableView):
    def __init__(self, parent: QWidget|None=None):
        QTableView.__init__(self, parent)
        self._annotations: AnnotationListModel|None = None
        self._time_window: TimeWindowModel|None = None
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.set_context(None, None)

    def set_context(self, time_window: TimeWindowModel|None, annotations: AnnotationListModel):
        if self._time_window is not None:
            pass
        self._time_window = time_window
        self._annotations = annotations
        if self._time_window is not None:
            self.setModel(ValueGridModel(annotations, time_window))
        else:
            self.setModel(None)
