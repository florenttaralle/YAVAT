from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
# ##################################################################
from src.models.annotation import AnnotationModel
from src.models.time_window import TimeWindowModel
from src.views.annotation_header import AnnotationHeaderView
from src.views.graph import GraphView
# ##################################################################


class AnnotationView(QWidget):
    def __init__(self, annotation: AnnotationModel, time_window: TimeWindowModel, 
                 header: AnnotationHeaderView, graph: GraphView, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._annotation = annotation
        self._time_window = time_window
        self.setFixedHeight(50)

        self.setLayout(QHBoxLayout())
        self._header = header
        self._header.setFixedWidth(100)
        self.layout().addWidget(self._header)

        self._graph  = graph
        self._graph.setFixedHeight(50)
        self.layout().addWidget(self._graph)
        self.layout().setContentsMargins(0, 2, 2, 2)
        self._header.setFixedWidth(200)
        
        header.edit.connect(self.onHeaderEdit)
        graph.click.connect(self.onGraphClick)
        graph.context_menu.connect(self.onGraphContextMenu)
        graph.double_click.connect(self.onGraphDoubleClick)
        
    def onHeaderEdit(self):
        self._annotation.set_selected(True)

    def onGraphClick(self, frame_id: int, event):
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        self._annotation.set_selected(True)

    def onGraphContextMenu(self, frame_id: int, event):
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        self._annotation.set_selected(True)

    def onGraphDoubleClick(self, frame_id: int, event):
        self._annotation.set_selected(True)
