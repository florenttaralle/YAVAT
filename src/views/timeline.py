from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu
from PyQt6.QtGui import QCursor, QContextMenuEvent
from functools import partial

from src.models.timeline import TimeLineModel, EventModel
from src.models.time_window import TimeWindowModel
from src.views.range_event import RangeEventView, RangeEventModel
from src.views.ponctual_event import PonctualEventView, PonctualEventModel
from src.widgets.graph import Graph, QWheelEvent
from src.icons import Icons

class TimeLineHeaderView(QWidget):
    def __init__(self, timeline: TimeLineModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._timeline = timeline
        self.setLayout(QVBoxLayout())
        self._name_lbl = QLabel(timeline.name)
        self._name_lbl.font().setBold(True)
        self._name_lbl.setWordWrap(True)
        self.layout().addWidget(self._name_lbl)
        timeline.name_changed.connect(self._name_lbl.setText)

class TimeLineView(QWidget):
    def __init__(self, timeline: TimeLineModel, time_window: TimeWindowModel, event_h: float=0.8, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._timeline = timeline
        self._time_window = time_window
        self.setLayout(QHBoxLayout())
        self._header = TimeLineHeaderView(timeline)
        self.layout().addWidget(self._header)
        self._header.setFixedWidth(100)
        self._graph  = Graph(0, 0, timeline.duration, 1)
        self._event_h = event_h
        self.layout().addWidget(self._graph)
        self._event_views = [self._event_view_factory(event) for event in timeline]

        self._graph.context_menu.connect(self.onGraphContextMenu)
        self._timeline.event_added.connect(self.onTimelineEventAdded)
        self._timeline.event_removed.connect(self.onTimelineEventRemoved)
        self._time_window.changed.connect(self._graph.set_time_window)
        self._graph.wheel_down.connect(self.onGraphWheelDown)
        self._graph.wheel_up.connect(self.onGraphWheelUp)
               
    @property
    def timeline(self) -> TimeLineModel:
        return self._timeline
    
    def _event_view_factory(self, event):
        if isinstance(event, RangeEventModel):
            view = RangeEventView(event, .5, self._event_h, .2, .1) 
        else:
            view = PonctualEventView(event, .5, self._event_h, .4, .1)
        self._graph.addItem(view)
        view.double_click.connect(self.onEventViewDoubleClick)
        return view

    def onEventViewDoubleClick(self, view, frame_id, event):
        print(f"onEventViewDoubleClick {view.model}")

    def _event_to_view(self, event: EventModel):
        for view in self._event_views:
            if view.model == event:
                return view
        raise ValueError()

    def onTimelineEventAdded(self, event: EventModel):
        view = self._event_view_factory(event)
        self._event_views.append(view)

    def onTimelineEventRemoved(self, event: EventModel):
        view = self._event_to_view(event)
        self._graph.removeItem(view)
        self._event_views.remove(view)

    def onGraphWheelUp(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._time_window.zoom_out()

    def onGraphWheelDown(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._time_window.zoom_in()

    def onGraphContextMenu(self, frame_id: float, event: QContextMenuEvent):
        frame_id = round(frame_id)
        if (frame_id < 0) or (frame_id > self._time_window.duration):
            return
        menu = QMenu()
        model = self._timeline.at_frame_id(frame_id)
        if model is not None:        
            action = menu.addAction(Icons.Delete.icon(), "Delete This Event")
            action.triggered.connect(partial(self.onMenuDeleteEvent, model))
            if isinstance(model, PonctualEventModel):
                action = menu.addAction(Icons.Range.icon(), "Convert To Range Event From Here")
                action.setEnabled(self._timeline.at_frame_id(model.frame_id + 1) is None)
                action.triggered.connect(partial(self.onMenuConvertToRange, model))
            else:
                action = menu.addAction(Icons.Ponctual.icon(), "Convert To Ponctual Event Here")
                action.triggered.connect(partial(self.onMenuConvertToPonctual, model, frame_id))
        else:
            action = menu.addAction(Icons.AddRange.icon(), "New Range Event From Here")
            action.setEnabled(self._timeline.can_add_range(frame_id, frame_id + 1))
            action.triggered.connect(partial(self.onMenuCreateRange, frame_id))
            action = menu.addAction(Icons.AddPonctual.icon(), "New Ponctual Event Here")
            action.setEnabled(self._timeline.can_add_ponctual(frame_id))
            action.triggered.connect(partial(self.onMenuCreatePonctual, frame_id))
        menu.exec(QCursor.pos())

    def onMenuCreateRange(self, frame_id):
        self._timeline.add_range(frame_id, frame_id+1)

    def onMenuCreatePonctual(self, frame_id):
        self._timeline.add_ponctual(frame_id)

    def onMenuDeleteEvent(self, event):
        self._timeline.rem(event)
    
    def onMenuConvertToRange(self, event):
        self._timeline.rem(event)
        self._timeline.add_range(event.frame_id, event.frame_id+1, event.label)
    
    def onMenuConvertToPonctual(self, event, frame_id):
        self._timeline.rem(event)
        self._timeline.add_ponctual(frame_id, event.label)
    
    