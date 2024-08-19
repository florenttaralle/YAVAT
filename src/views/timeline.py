from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QContextMenuEvent, QColor
# ##################################################################
from src.models.timeline import TimelineModel, EventModel
from src.models.time_window import TimeWindowModel
from src.views.timeline_header import TimelineHeaderView
from src.views.timeline_graph import TimelineGraphView
from src.views.event import EventView
from src.views.timeline_contextual_menu import TimelineContextualMenu
# ##################################################################


class TimelineView(QWidget):
    COLOR = QColor("#346beb")

    edit_timeline_name = pyqtSignal(TimelineModel)
    "SIGNAL: edit_timeline_name(timeline: TimelineModel)"
    edit_event = pyqtSignal(EventModel)
    "SIGNAL: edit_event(event: EventModel)"
    
    def __init__(self, timeline: TimelineModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        QWidget.__init__(self, parent)
        self._timeline = timeline
        self._time_window = time_window
        self.setLayout(QHBoxLayout())
        self._header = TimelineHeaderView(timeline)
        self._header.setFixedWidth(100)
        self.layout().addWidget(self._header)
        self._graph  = TimelineGraphView(time_window, self.COLOR)
        self._graph.setFixedHeight(50)
        self.layout().addWidget(self._graph)
        self.layout().setContentsMargins(0, 2, 2, 2)
        self._header.setFixedWidth(150)
        # context menu
        self._context_menu = TimelineContextualMenu(timeline, time_window)
        # connect signals/slots
        self._header.edit_timeline_name.connect(self.edit_timeline_name)
        self._graph.context_menu.connect(self.onGraphContextMenu)
        self._timeline.event_added.connect(self.onTimelineEventAdded)
        self._timeline.event_removed.connect(self.onTimelineEventRemoved)
        # populate existing events
        self._event_views = [self._event_view_factory(event) for event in timeline]
               
    @property
    def timeline(self) -> TimelineModel:
        return self._timeline
    
    def _event_view_factory(self, event: EventModel) -> EventView:
        view = EventView(event, self.COLOR)
        self._graph.addItem(view)
        view.double_click.connect(self.edit_event)
        return view

    def _event_to_view(self, event: EventModel):
        for view in self._event_views:
            if view._event == event:
                return view
        raise ValueError()

    def onTimelineEventAdded(self, event: EventModel):
        view = self._event_view_factory(event)
        self._event_views.append(view)

    def onTimelineEventRemoved(self, event: EventModel):
        view = self._event_to_view(event)
        self._graph.removeItem(view)
        self._event_views.remove(view)

    def onGraphContextMenu(self, frame_id: float, event: QContextMenuEvent):
        frame_id = round(frame_id)
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        self._context_menu.show(frame_id)
        event.accept()

