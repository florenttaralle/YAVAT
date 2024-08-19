from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QToolBar
from PyQt6.QtGui import QAction, QKeySequence
from typing import Callable
# ##############################################################
from src.models.timeline_list import TimelineListModel
from src.models.timeline_list_state import TimelineListState
from src.models.timeline import TimelineModel, EventModel
from src.models.time_window import TimeWindowModel
from src.models.event import EventModel
from src.icons import Icons
# ##############################################################


class TimelineListBarView(QToolBar):
    edit_timeline_name = pyqtSignal(TimelineModel)
    "SIGNAL: edit_timeline_name(timeline: TimelineModel)"
    edit_event = pyqtSignal(EventModel)
    "SIGNAL: edit_event(event: EventModel)"

    def __init__(self, timeline_list: TimelineListModel, state: TimelineListState, 
                 time_window: TimeWindowModel, parent: QWidget|None = None):
        QToolBar.__init__(self, parent)
        self._timeline_list         = timeline_list
        self._state                 = state
        self._time_window           = time_window
        self._crt_timeline          = None
        self._crt_event:            EventModel|None = None  # event at current frame_id
        self._prv_event:            EventModel|None = None  # event before crt_event or frame_id
        self._nxt_event:            EventModel|None = None  # event after crt_event or frame_id
        self.setMovable(False)
        self._here_to_left_target:  int|None = None
        self._here_to_right_target: int|None = None
        self._left_to_here_target:  Callable[[int]]|None = None
        self._right_to_here_target: Callable[[int]]|None = None

        # TIMELINE ADD/REM
        self._act_timeline_add = QAction()
        self._act_timeline_add.setIcon(Icons.TimelineAdd.icon())
        self._act_timeline_add.triggered.connect(self.onActTimelineAdd)
        self._act_timeline_add.setToolTip("Add a new Timeline (T)")
        self._act_timeline_add.setShortcut(Qt.Key.Key_T)
        self.addAction(self._act_timeline_add)
        self._act_timeline_edit = QAction()
        self._act_timeline_edit.setIcon(Icons.Edit.icon())
        self._act_timeline_edit.triggered.connect(self.onActTimelineEdit)
        self._act_timeline_edit.setToolTip("Edit Timeline Name")
        self.addAction(self._act_timeline_edit)
        self._act_timeline_rem = QAction()
        self._act_timeline_rem.setIcon(Icons.TimelineRem.icon())
        self._act_timeline_rem.triggered.connect(self.onActTimelineRem)
        self._act_timeline_rem.setToolTip("Delete Timeline")
        self.addAction(self._act_timeline_rem)
        self.addSeparator()

        # ZOOM IN/OUT Reset View
        self._act_reset_zoom = QAction()
        self._act_reset_zoom.setIcon(Icons.ZoomReset.icon())
        self._act_reset_zoom.triggered.connect(time_window.reset)
        self._act_reset_zoom.setToolTip("Reset View")
        self.addAction(self._act_reset_zoom)
        self._act_zoom_in = QAction()
        self._act_zoom_in.setIcon(Icons.ZoomIn.icon())
        self._act_zoom_in.triggered.connect(time_window.zoom_in)
        self._act_zoom_in.setToolTip("Zoom In (+)")
        self._act_zoom_in.setShortcut(Qt.Key.Key_Plus)
        self.addAction(self._act_zoom_in)
        self._act_zoom_out = QAction()
        self._act_zoom_out.setIcon(Icons.ZoomOut.icon())
        self._act_zoom_out.triggered.connect(time_window.zoom_out)
        self._act_zoom_out.setToolTip("Zoom Out (-)")
        self._act_zoom_out.setShortcut(Qt.Key.Key_Minus)
        self.addAction(self._act_zoom_out)
        self.addSeparator()

        # Add/Edit/Rem Event Here
        self._act_add_event_here = QAction()
        self._act_add_event_here.setIcon(Icons.EventAdd.icon())
        self._act_add_event_here.triggered.connect(self.onActAddEventHere)
        self._act_add_event_here.setToolTip("Add a Range Event here (E)")
        self._act_add_event_here.setShortcut(Qt.Key.Key_E)
        self.addAction(self._act_add_event_here)
        self._act_edit_event_here = QAction()
        self._act_edit_event_here.setIcon(Icons.EventInfo.icon())
        self._act_edit_event_here.triggered.connect(self.onActEditCrtEvent)
        self._act_edit_event_here.setToolTip("Edit Event at current time position (L)")
        self._act_edit_event_here.setShortcut(Qt.Key.Key_L)
        self.addAction(self._act_edit_event_here)
        self._act_rem_event_here = QAction()
        self._act_rem_event_here.setIcon(Icons.EventRem.icon())
        self._act_rem_event_here.triggered.connect(self.onActRemCrtEvent)
        self._act_rem_event_here.setToolTip("Remove Event at current time position (Delete)")
        self._act_rem_event_here.setShortcut(Qt.Key.Key_Delete)
        self.addAction(self._act_rem_event_here)
        self.addSeparator()

        # Change Current Event Bounds
        self._act_left_to_here = QAction()
        self._act_left_to_here.setIcon(Icons.ArrowToRight.icon())
        self._act_left_to_here.triggered.connect(self.onActLeftToHere)
        self._act_left_to_here.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Right))
        self.addAction(self._act_left_to_here)
        self._act_right_to_here = QAction()
        self._act_right_to_here.setIcon(Icons.ArrowToLeft.icon())
        self._act_right_to_here.triggered.connect(self.onActRightToHere)
        self._act_right_to_here.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Left))
        self.addAction(self._act_right_to_here)
        self.addSeparator()

        # Goto Bounds
        self._act_here_to_left = QAction()
        self._act_here_to_left.setIcon(Icons.ArrowFromRight.icon())
        self._act_here_to_left.triggered.connect(self.onActHereToLeft)
        self._act_here_to_left.setShortcut(QKeySequence(Qt.Modifier.SHIFT | Qt.Key.Key_Left))
        self.addAction(self._act_here_to_left)
        self._act_here_to_right = QAction()
        self._act_here_to_right.setIcon(Icons.ArrowFromLeft.icon())
        self._act_here_to_right.triggered.connect(self.onActHereToRight)
        self._act_here_to_right.setShortcut(QKeySequence(Qt.Modifier.SHIFT | Qt.Key.Key_Right))
        self.addAction(self._act_here_to_right)
        self.addSeparator()

        state.selection_changed.connect(self._crt_timeline_changed)
        time_window.playing_changed.connect(self.onTimeWindowPlayingChanged)
        time_window.position_changed.connect(self._update_events_n_actions)
        state.selection_changed.connect(self.onTimelineListSelectedChanged)
        self._crt_timeline_changed(state.selection)
        self._reset_events()
        self._update_actions()

    def _crt_timeline_changed(self, timeline: TimelineModel|None):
        if self._crt_timeline is not None:
            self._crt_timeline.event_added.disconnect(self._update_events_n_actions)
            self._crt_timeline.event_removed.disconnect(self._update_events_n_actions)
        self._crt_timeline = timeline
        if self._crt_timeline is not None:
            self._crt_timeline.event_added.connect(self._update_events_n_actions)
            self._crt_timeline.event_removed.connect(self._update_events_n_actions)
        self._act_timeline_rem.setEnabled(timeline is not None)

    def _set_crt_event(self, event: EventModel|None):
        if self._crt_event is not None:
            self._crt_event.first_changed.disconnect(self._update_events_n_actions)
            self._crt_event.last_changed.disconnect(self._update_events_n_actions)
        self._crt_event = event
        if self._crt_event is not None:
            self._crt_event.first_changed.connect(self._update_events_n_actions)
            self._crt_event.last_changed.connect(self._update_events_n_actions)            

    def _set_prv_event(self, event: EventModel|None):
        if self._prv_event is not None:
            self._prv_event.last_changed.disconnect(self._update_events_n_actions)
        self._prv_event = event
        if self._prv_event is not None:
            self._prv_event.last_changed.connect(self._update_events_n_actions)
        
    def _set_nxt_event(self, event: EventModel|None):
        if self._nxt_event is not None:
            self._nxt_event.first_changed.disconnect(self._update_events_n_actions)
        self._nxt_event = event
        if self._nxt_event is not None:
            self._nxt_event.first_changed.connect(self._update_events_n_actions)

    def _event_or_none(self, event: EventModel|int|None) -> EventModel|None:
        return event if isinstance(event, EventModel) else None

    def _reset_events(self):
        prv_event, crt_event, nxt_event = None, None, None
        if self._crt_timeline is not None:
            frame_id = self._time_window.position
            crt_event = self._crt_timeline.at_frame_id(frame_id)
            if crt_event is None:
                prv_event = self._crt_timeline.before_frame_id(frame_id)
                nxt_event = self._crt_timeline.after_frame_id(frame_id)
            else:
                prv_event = self._event_or_none(crt_event.prv_event)
                nxt_event = self._event_or_none(crt_event.nxt_event)
        self._set_prv_event(prv_event)
        self._set_crt_event(crt_event)
        self._set_nxt_event(nxt_event)

    def _update_actions(self):
        # disable the whole bar when playing
        self.setEnabled(not self._time_window.playing)
        if self._time_window.playing: return
        
        if self._crt_timeline is not None:
            frame_id = self._time_window.position
            # A timeline is selected
            self._act_timeline_edit.setEnabled(True)
            self._act_timeline_rem.setEnabled(True)
            self._act_add_event_here.setEnabled(self._crt_timeline.can_add(frame_id, frame_id))
            self._act_edit_event_here.setEnabled(self._crt_event is not None)
            self._act_rem_event_here.setEnabled(self._crt_event is not None)            
            # from here to left
            if (self._crt_event is not None) and (frame_id != self._crt_event.first):
                self._act_here_to_left.setToolTip("Goto Current Event's Start (Shit+Left)")
                self._here_to_left_target = self._crt_event.first
            else:
                self._act_here_to_left.setToolTip("Goto Previous Event's End (Shift+Left)")
                self._here_to_left_target = self._prv_event.last if self._prv_event else None
            self._act_here_to_left.setEnabled(self._here_to_left_target is not None)
            # from here to right
            if (self._crt_event is not None) and (frame_id != self._crt_event.last):                            
                self._act_here_to_right.setToolTip("Goto Current Event's End (Shift+Right)")
                self._here_to_right_target = self._crt_event.last
            else:
                self._act_here_to_right.setToolTip("Goto Next Event's Start (Shift+Right)")
                self._here_to_right_target = self._nxt_event.first if self._nxt_event else None
            self._act_here_to_right.setEnabled(self._here_to_right_target is not None)       
            # event to here (move events boundaries)
            if self._crt_event is not None:
                self._act_left_to_here.setToolTip("Move Current Event's Start to here (Ctrl+Shit+Right)")
                self._left_to_here_target = self._crt_event.set_first \
                    if frame_id != self._crt_event.first \
                    else None
                self._act_right_to_here.setToolTip("Move Current Event's End to here (Ctrl+Shift+Left)")
                self._right_to_here_target = self._crt_event.set_last \
                    if frame_id != self._crt_event.last \
                    else None
            else:
                self._act_left_to_here.setToolTip("Move Previous Event's End to here (Ctrl+Shift+Right)")
                self._left_to_here_target = self._prv_event.set_last if self._prv_event else None
                self._act_right_to_here.setToolTip("Move Next Event's Start to here (Ctrl+Shift+Left)")
                self._right_to_here_target = self._nxt_event.set_first if self._nxt_event else None
            self._act_left_to_here.setEnabled(self._left_to_here_target is not None)
            self._act_right_to_here.setEnabled(self._right_to_here_target is not None)
                
        else:
            # No timeline selected
            self._act_timeline_rem.setEnabled(False)
            self._act_timeline_edit.setEnabled(False)
            self._act_add_event_here.setEnabled(False)
            self._act_edit_event_here.setEnabled(False)
            self._act_rem_event_here.setEnabled(False)
            self._act_left_to_here.setEnabled(False)
            self._act_right_to_here.setEnabled(False)
            self._act_here_to_left.setEnabled(False)
            self._act_here_to_right.setEnabled(False)

    # TIMELINE / EVENTS SIGNALS
    # #######################################################################
    def onTimeWindowPlayingChanged(self, playing: bool):
        if not playing:
            self._reset_events()
        self._update_actions()

    def onTimelineListSelectedChanged(self, timeline: TimelineModel|None):
        if self._time_window.playing: return
        self._reset_events()
        self._update_actions()

    def _update_events_n_actions(self, *_):
        if self._time_window.playing: return
        self._reset_events()
        self._update_actions()

    # ACTIONS
    # #######################################################################
    def onActTimelineAdd(self, checked: bool):
        self._timeline_list.add()

    def onActTimelineEdit(self, checked: bool):
        self.edit_timeline_name.emit(self._crt_timeline)

    def onActTimelineRem(self, checked: bool):
        self._timeline_list.rem(self._crt_timeline)
        
    def onActAddEventHere(self, checked: bool):
        self._crt_timeline.add(self._time_window.position, self._time_window.position)
        
    def onActEditCrtEvent(self, checked: bool):
        self.edit_event.emit(self._crt_event)

    def onActRemCrtEvent(self, checked: bool):
        self._crt_timeline.rem(self._crt_event)
    
    def onActLeftToHere(self, checked: bool):
        self._left_to_here_target(self._time_window.position)

    def onActRightToHere(self, checked: bool):
        self._right_to_here_target(self._time_window.position)

    def onActHereToLeft(self, checked: bool):
        self._time_window.position = self._here_to_left_target
            
    def onActHereToRight(self, checked: bool):
        self._time_window.position = self._here_to_right_target
