from PyQt6.QtWidgets import QWidget
# ##################################################################
from src.models.time_window import TimeWindowModel
from src.models.timeline import TimelineModel, EventModel
from src.models.annotation_watchers import AnnotationWatcherSingleton, AnnotationValueWatcherModel
from src.views.annotation import AnnotationView, AnnotationHeaderView
from src.views.timeline_graph import TimelineGraphView
from src.views.dialogs.event_editor import EventEditorDialog
from src.views.contextual_menus.time_window import TimeWindowContextualMenu, QMenu, QCursor
from src.views.contextual_menus.timeline import TimelineContextualMenu
# ##################################################################


class TimelineView(AnnotationView):
    def __init__(self, timeline: TimelineModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        header  = AnnotationHeaderView(timeline, True)
        graph   = TimelineGraphView(time_window, timeline)
        AnnotationView.__init__(self, timeline, time_window, header, graph, parent)
        self._watcher = AnnotationWatcherSingleton.get_or_create(
            AnnotationValueWatcherModel, timeline, time_window)
        self._watcher.value_changed.connect(self.onValueChanged)
        self._set_value(self._watcher.value)

    @property
    def timeline(self) -> TimelineModel:
        return self._annotation

    def _set_value(self, value: str|None):
        self._header._value_lbl.setText((value or "") + " >")
    
    def onValueChanged(self, timeline: TimelineModel, frame_id: int, value: float|None):
        self._set_value(value)

    def onGraphContextMenu(self, frame_id: int, cm_event):
        AnnotationView.onGraphContextMenu(self, frame_id, cm_event)
        if (frame_id < 0) or (frame_id > self._time_window.duration): return
        menu    = QMenu()
        tw_menu = TimeWindowContextualMenu(self._time_window, frame_id).attach(menu)
        menu.addSeparator()
        tl_menu = TimelineContextualMenu(self._time_window, self._annotation, frame_id).attach(menu)
        menu.exec(QCursor.pos())
    
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
