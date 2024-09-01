from PyQt6.QtWidgets import QWidget, QGraphicsRectItem
from PyQt6.QtGui import QColorConstants, QPen, QColor
from typing import Mapping
from src.models.timeline import TimelineModel, EventModel
from src.views.graph import GraphView, TimeWindowModel
from src.views.event import EventView

class TimelineGraphView(GraphView):
    def __init__(self, time_window: TimeWindowModel, timeline: TimelineModel, parent: QWidget|None=None):
        GraphView.__init__(self, time_window, parent)
        self.setYRange(0, 1, .05)
        self._timeline = timeline
        self._views: Mapping[EventModel, EventView] = {}

        # add the border
        self._border = QGraphicsRectItem(0, .1, time_window.duration-1, .8)
        self._border.setBrush(QColorConstants.Transparent)
        self.onTimelineColorChanged(timeline.color)
        self._border.setOpacity(.6)
        self.addItem(self._border)

        # add existing events
        for event in timeline:
            self.onEventAdded(event)

        # connect signals & slots
        self._timeline.event_added.connect(self.onEventAdded)
        self._timeline.event_removed.connect(self.onEventRemoved)
        self._timeline.color_changed.connect(self.onTimelineColorChanged)
        
    def onTimelineColorChanged(self, color: QColor):
        pen = QPen(color)
        pen.setWidth(4)
        pen.setCosmetic(True)
        self._border.setPen(pen)

    def onEventAdded(self, event: EventModel):
        view = EventView(event, self._timeline.color)
        view.left_click.connect(self.onEventLeftClick)
        self._timeline.color_changed.connect(view.set_color)
        self._views[event] = view
        self.addItem(view)
    
    def onEventLeftClick(self, event: EventModel, frame_id: int):
        self._time_window.goto(frame_id)

    def onEventRemoved(self, event: EventModel):
        view = self._views[event]
        view.left_click.disconnect(self.onEventLeftClick)
        self._timeline.color_changed.disconnect(view.set_color)
        del self._views[event]
        self.removeItem(view)
