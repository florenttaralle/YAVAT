from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
# ##################################################################
from src.models.annotation import AnnotationModel
from src.models.time_window import TimeWindowModel
from src.views.annotation_header import AnnotationHeaderView
from src.views.graph import GraphView
from src.widgets.spacer import Spacer
# ##################################################################

class AnnotationView(QSplitter):
    def __init__(self, annotation: AnnotationModel, time_window: TimeWindowModel, 
                 header: AnnotationHeaderView, graph: GraphView, parent: QWidget|None = None):
        QSplitter.__init__(self, Qt.Orientation.Horizontal, parent)
        self._annotation = annotation
        self._time_window = time_window
        self.setChildrenCollapsible(False)
        self.setContentsMargins(0, 5, 5, 5)
        self.setFixedHeight(60)

        self._header = header
        self._header.setMinimumWidth(200)
        self.addWidget(self._header)

        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        widget.layout().setSpacing(0)
        widget.layout().setContentsMargins(0, 0, 0, 0)
        widget.layout().addWidget(Spacer())
        self._graph  = graph
        widget.layout().addWidget(self._graph)
        widget.layout().addWidget(Spacer())
        self.addWidget(widget)
        
        graph.click.connect(self.onGraphClick)
        graph.context_menu.connect(self.onGraphContextMenu)
        graph.double_click.connect(self.onGraphDoubleClick)
        
    def onGraphClick(self, frame_id: int, event):
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        self._annotation.set_selected(True)

    def onGraphContextMenu(self, frame_id: int, event):
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        self._annotation.set_selected(True)

    def onGraphDoubleClick(self, frame_id: int, event):
        self._annotation.set_selected(True)
