from PyQt6.QtCore import QObject, pyqtSignal
from bisect import bisect_left
from .annotation_watcher import AnnotationWatcherModel
from src.models.time_window import TimeWindowModel
from src.models.annotation import AnnotationModel
from src.models.timeline import TimelineModel, EventModel

class AnnotationValueWatcherModel(AnnotationWatcherModel):
    value_changed = pyqtSignal(object, int, object)
    "SIGNAL: value_changed(annotation: AnnotationModel, frame_id: int, value: object)"
    
    def __init__(self, annotation: AnnotationModel, time_window: TimeWindowModel):
        AnnotationWatcherModel.__init__(self, annotation)
        self._time_window       = time_window
        self._last_frame_id:    int = None
        self._last_value        = None
        self._connect()
        self._update()

    def _connect(self):
        self._time_window.position_changed.connect(self._update)
        if isinstance(self.annotation, TimelineModel):
            self.annotation.event_added.connect(self.onTimelineEventAdded)
            self.annotation.event_removed.connect(self.onTimelineEventRemoved)
            for event in self.annotation:
                self.onTimelineEventAdded(event)

    def _disconnect(self):
        self._time_window.position_changed.disconnect(self._update)
        if isinstance(self.annotation, TimelineModel):
            self.annotation.event_added.disconnect(self.onTimelineEventAdded)
            self.annotation.event_removed.disconnect(self.onTimelineEventRemoved)
            for event in self.annotation:
                self.onTimelineEventRemoved(event)

    @property
    def value(self):
        return self._last_value

    def _update(self, *_):
        frame_id = self._time_window.position
        if frame_id != self._last_frame_id:
            self._last_frame_id = frame_id
            if isinstance(self.annotation, TimelineModel):            
                self._last_value = self._timeline_value(frame_id)
            else:
                self._last_value = self._timeseries_value(frame_id)
            self.value_changed.emit(self.annotation, self._last_frame_id, self._last_value)

    def onTimelineEventAdded(self, event: EventModel):
        event.first_changed.connect(self._update)
        event.last_changed.connect(self._update)
        self._update()

    def onTimelineEventRemoved(self, event: EventModel):
        event.first_changed.disconnect(self._update)
        event.last_changed.disconnect(self._update)
        self._update()

    def _timeseries_value(self, frame_id: int):
        key         = lambda xy_value: round(xy_value.x)
        xy_values   = self.annotation.xy_values
        index       = bisect_left(xy_values, frame_id, key=key)
        if (index < len(xy_values)) and (key(xy_values[index]) == frame_id):
            return xy_values[index].y
        else:
            return None
    
    def _timeline_value(self, frame_id: int):
        event: EventModel|None = self.annotation.at_frame_id(frame_id)
        return event.label if event is not None else None
