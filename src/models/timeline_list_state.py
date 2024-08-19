from typing import Mapping, List
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.timeline_list import TimelineListModel, TimelineModel


class TimelineState(QObject):
    selected_changed = pyqtSignal(TimelineModel, bool)
    "SIGNAL: selected_changed(timeline: TimelineModel, selected: bool)"
    visible_changed = pyqtSignal(TimelineModel, bool)
    "SIGNAL: visible_changed(timeline: TimelineModel, selected: bool)"

    def __init__(self, timeline: TimelineModel, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._timeline  = timeline
        self._selected  = False
        self._visible   = True

    @property
    def selected(self) -> bool:
        return self._selected
    def set_selected(self, selected: bool):
        if selected != self._selected:
            self._selected = selected
            self.selected_changed.emit(self._timeline, selected)
    def select(self):   self.set_selected(True)
    def deselect(self): self.set_selected(False)

    @property
    def visible(self) -> bool:
        return self._visible    
    def set_visible(self, visible: bool):
        if visible != self._visible:
            self._visible = visible
            self.visible_changed.emit(self._timeline, visible)
    def show(self): self.set_visible(True)
    def hide(self): self.set_visible(False)



class TimelineListState(QObject):
    selection_changed = pyqtSignal(object)
    "SIGNAL: selection_changed(TimelineModel|None)"
    timeline_added              = pyqtSignal(TimelineModel)
    "SIGNAL: timeline_added(timeline: TimelineModel)"
    timeline_removed            = pyqtSignal(TimelineModel)
    "SIGNAL: timeline_removed(timeline: TimelineModel)"

    def __init__(self, timeline_list: TimelineListModel, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._timeline_list         = timeline_list
        self._selection:            TimelineModel|None = None
        self._states:               Mapping[TimelineModel, TimelineState] = {}
        for timeline in timeline_list:
            self.onTimelineAdded(timeline)
        timeline_list.timeline_added.connect(self.onTimelineAdded)
        timeline_list.timeline_removed.connect(self.onTimelineRemoved)
  
    @property
    def states(self) -> List[TimelineState]:
        return self._states.values()
    
    @property
    def selection(self) -> TimelineModel|None:
        return self._selection
    def set_selection(self, selection: TimelineModel|None):
        if selection != self._selection:
            self._selection = selection
            self.selection_changed.emit(selection)

    def __getitem__(self, timeline: TimelineModel) -> TimelineState:
        return self._states[timeline]
    
    def onSelectedChanged(self, timeline: TimelineModel, selected: bool):
        self.set_selection(timeline if selected else None)
    
    def onTimelineAdded(self, timeline: TimelineModel):
        state = TimelineState(timeline)
        state.selected_changed.connect(self.onSelectedChanged)
        self._states[timeline] = state
        self.timeline_added.emit(timeline)
    
    def onTimelineRemoved(self, timeline: TimelineModel):
        self._states[timeline].deselect()
        del self._states[timeline]
        self.timeline_removed.emit(timeline)
