from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsSceneMouseEvent, QMenu, QAction
from src.models.timeline import TimeLineModel, EventModel
from src.views.range_event import RangeEventView, RangeEventModel
from src.views.ponctual_event import PonctualEventView, PonctualEventModel
from src.graph import Graph, QMouseEvent

class TimeLineHeaderView(QWidget):
    def __init__(self, timeline: TimeLineModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._timeline = timeline
        self.setLayout(QVBoxLayout())
        self._name_lbl = QLabel(timeline.name)
        self._name_lbl.font().setBold(True)
        self._name_lbl.setStyleSheet("QLabel {color: #0000FF}")
        self.layout().addWidget(self._name_lbl)
        timeline.name_changed.connect(self._name_lbl.setText)

class TimeLineView(QWidget):
    def __init__(self, timeline: TimeLineModel, y: float=1, h: float=2, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._timeline = timeline
        self.setLayout(QHBoxLayout())
        self._header = TimeLineHeaderView(timeline)
        self.layout().addWidget(self._header)
        self._header.setFixedWidth(150)
        self._graph  = Graph(0, timeline.duration, 2)
        self.layout().addWidget(self._graph)
        self._event_views = [self._event_view_factory(event) for event in timeline]

        self._graph.click.connect(self.onGraphClick)
        self._timeline.event_added.connect(self.onTimelineEventAdded)
        self._timeline.event_removed.connect(self.onTimelineEventRemoved) 
               
    def _event_view_factory(self, event):
        if isinstance(event, RangeEventModel):
            view = RangeEventView(event, 1, 1, .2, .1) 
        else:
            view = PonctualEventView(event, 1, 1, .4, .1)
        self._graph.addItem(view)
        view.right_click.connect(self.onEventViewRightClick)
        return view

    def _event_to_view(self, event: EventModel):
        for view in self._event_views:
            if view._model == event:
                return view
        raise ValueError()

    def onTimelineEventAdded(self, event: EventModel):
        view = self._event_view_factory(event)
        self._event_views.append(view)

    def onTimelineEventRemoved(self, event: EventModel):
        view = self._event_to_view(event)
        self._graph.removeItem(view)
        self._event_views.remove(view)

    def onEventViewRightClick(self, view, frame_id: int, event: QGraphicsSceneMouseEvent):
        menu = QMenu()
        
        action = menu.addAction("Delete")
        def onDeleteAction(_): self._timeline.rem(view._model)
        action.triggered.connect(onDeleteAction)
        
        if isinstance(view._model, PonctualEventModel):
            action = menu.addAction("Convert To Range Event")
            action.setEnabled(self._timeline.at_frame_id(view._model.frame_id + 1) is None)
            def onConvertToRangeAction(_): 
                self._timeline.rem(view._model)
                self._timeline.add_range(view._model.frame_id, view._model.frame_id+1, view._model.label)
            action.triggered.connect(onConvertToRangeAction)
        else:
            action = menu.addAction("Convert To Ponctual Event")
            def onConvertToPonctualAction(_): 
                self._timeline.rem(view._model)
                self._timeline.add_ponctual(frame_id, view._model.label)
            action.triggered.connect(onConvertToPonctualAction)
            
        menu.exec(event.screenPos())
        
    def onGraphClick(self, frame_id: float, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()

            action = menu.addAction("New Range Event")
            action.setEnabled(self._timeline.can_add_range(frame_id, frame_id + 1))
            def onNewRangeEvent(_): self._timeline.add_range(frame_id, frame_id+1)
            action.triggered.connect(onNewRangeEvent)

            action = menu.addAction("New Ponctual Event")
            action.setEnabled(self._timeline.can_add_ponctual(frame_id))
            def onNewPonctualEvent(_):  self._timeline.add_ponctual(frame_id)
            action.triggered.connect(onNewPonctualEvent)

            menu.exec(event.globalPos())
            