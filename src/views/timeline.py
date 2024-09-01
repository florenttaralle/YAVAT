from PyQt6.QtWidgets import QWidget
# ##################################################################
from src.models.time_window import TimeWindowModel
from src.models.timeline import TimelineModel, EventModel
from src.views.annotation import AnnotationView, AnnotationHeaderView
from src.views.timeline_graph import TimelineGraphView
from src.views.dialogs.timeline_editor import TimelineEditorDialog
from src.views.dialogs.event_editor import EventEditorDialog
from src.views.contextual_menus.timeline import TimelineContextualMenu
# ##################################################################


class TimelineView(AnnotationView):
    def __init__(self, timeline: TimelineModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        header  = AnnotationHeaderView(timeline)
        graph   = TimelineGraphView(time_window, timeline)
        AnnotationView.__init__(self, timeline, time_window, header, graph, parent)

    @property
    def timeline(self) -> TimelineModel:
        return self._annotation
    
    def onHeaderEdit(self):
        AnnotationView.onHeaderEdit(self)
        TimelineEditorDialog().exec(self._annotation)

    def onGraphContextMenu(self, frame_id: int, cm_event):
        AnnotationView.onGraphContextMenu(self, frame_id, cm_event)
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        TimelineContextualMenu(self.timeline, self._time_window).show(frame_id)
    
    def onGraphDoubleClick(self, frame_id: int, m_event):
        AnnotationView.onGraphDoubleClick(self, frame_id, m_event)
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        crt_event = self.timeline.at_frame_id(frame_id)
        if crt_event is not None:
            EventEditorDialog().exec(crt_event)
        elif self.timeline.can_add(frame_id, frame_id):
            event = EventModel(frame_id, frame_id)
            self.timeline.add(event)
            self._time_window.goto(frame_id)
