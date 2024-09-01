from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
# ###########################################################
from src.models.time_window import TimeWindowModel
from src.models.annotation_list import AnnotationListModel
from src.views.annotation_list_bar import AnnotationListBar
from src.views.annotation_list_list import AnnotationListListView
# ###########################################################

class AnnotationListView(QWidget):
    def __init__(self, time_window: TimeWindowModel|None=None, annotations: AnnotationListModel|None=None, parent: QWidget|None=None):
        QWidget.__init__(self, parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        self._bar = AnnotationListBar()
        layout.addWidget(self._bar)        
        self._list = AnnotationListListView()
        layout.addWidget(self._list)
        
        self.set_context(time_window, annotations)
        
    def set_context(self, time_window: TimeWindowModel|None, annotations: AnnotationListModel):
        self._bar.set_context(time_window, annotations)
        self._list.set_context(time_window, annotations)
