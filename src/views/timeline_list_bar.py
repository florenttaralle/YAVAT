from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QToolBar
from PyQt6.QtGui import QAction, QKeySequence
from typing import Callable
# ##############################################################
from src.models.timeline_list import TimeLineListModel, TimeLineModel
from src.models.time_window import TimeWindowModel
from src.models.event import EventModel
from src.models.range_event import RangeEventModel
from src.icons import Icons
# ##############################################################

class TimeLineListBarView(QToolBar):
    def __init__(self, timeline_list: TimeLineListModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        QToolBar.__init__(self, parent)
        self._timeline_list         = timeline_list
        self._time_window           = time_window
        self._crt_timeline:         TimeLineModel|None = None
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
        self._act_timeline_add.setIcon(Icons.Timeline.icon())
        self._act_timeline_add.triggered.connect(lambda _: timeline_list.add())
        self._act_timeline_add.setToolTip("Add a new TimeLine (T)")
        self._act_timeline_add.setShortcut(Qt.Key.Key_T)
        self.addAction(self._act_timeline_add)
        self._act_timeline_rem = QAction()
        self._act_timeline_rem.setIcon(Icons.Delete.icon())
        self._act_timeline_rem.triggered.connect(self.onActTimelineRem)
        self._act_timeline_rem.setToolTip("Delete TimeLine")
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

        # Add Event Here
        self._act_add_range_here = QAction()
        self._act_add_range_here.setIcon(Icons.AddRange.icon())
        self._act_add_range_here.triggered.connect(self.onActAddRangeHere)
        self._act_add_range_here.setToolTip("Add a Range Event here (R)")
        self._act_add_range_here.setShortcut(Qt.Key.Key_R)
        self.addAction(self._act_add_range_here)
        self._act_add_ponctual_here = QAction()
        self._act_add_ponctual_here.setIcon(Icons.AddPonctual.icon())
        self._act_add_ponctual_here.triggered.connect(self.onActAddPonctualHere)
        self._act_add_ponctual_here.setToolTip("Add a Ponctual Event here (P)")
        self._act_add_ponctual_here.setShortcut(Qt.Key.Key_P)
        self.addAction(self._act_add_ponctual_here)
        self.addSeparator()

        # Change/Delete Crt Event
        self._act_to_range_here = QAction()
        self._act_to_range_here.setIcon(Icons.Range.icon())
        self._act_to_range_here.triggered.connect(self.onActToRangeHere)
        self._act_to_range_here.setToolTip("Convert to Range Event from here (Ctrl+R)")
        self._act_to_range_here.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_R))
        self.addAction(self._act_to_range_here)
        self._act_to_ponctual_here = QAction()
        self._act_to_ponctual_here.setIcon(Icons.Ponctual.icon())
        self._act_to_ponctual_here.triggered.connect(self.onActToPonctualHere)
        self._act_to_ponctual_here.setToolTip("Convert to Ponctual Event here (Ctrl+P)")
        self._act_to_ponctual_here.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_P))
        self.addAction(self._act_to_ponctual_here)
        self._act_rem_crt_event = QAction()
        self._act_rem_crt_event.setIcon(Icons.Delete.icon())
        self._act_rem_crt_event.triggered.connect(self.onActRemCrtEvent)
        self._act_rem_crt_event.setToolTip("Delete Current Event (Ctrl+D)")
        self._act_rem_crt_event.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_D))
        self.addAction(self._act_rem_crt_event)
        self.addSeparator()

        # Change Current Bounds
        self._act_left_to_here = QAction()
        self._act_left_to_here.setIcon(Icons.ArrowToRight.icon())
        self._act_left_to_here.triggered.connect(self.onActLeftToHere)
        self._act_left_to_here.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Left))
        self.addAction(self._act_left_to_here)
        self._act_right_to_here = QAction()
        self._act_right_to_here.setIcon(Icons.ArrowToLeft.icon())
        self._act_right_to_here.triggered.connect(self.onActRightToHere)
        self._act_right_to_here.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Right))
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

        time_window.playing_changed.connect(self.onTimeWindowPlayingChanged)
        time_window.position_changed.connect(self._update_events_n_actions)
        timeline_list.selected_timeline_changed.connect(self.onTimeLineListSelectedChanged)
        self._set_crt_timeline(timeline_list.selected_timeline)
        self._reset_events()
        self._update_actions()


    def _set_crt_timeline(self, timeline: TimeLineModel|None):
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
            # A timeline is selected
            self._act_timeline_rem.setEnabled(True)
            frame_id = self._time_window.position
            self._act_add_range_here.setEnabled(self._crt_timeline.can_add_range(frame_id))
            self._act_add_ponctual_here.setEnabled(self._crt_timeline.can_add_ponctual(frame_id))
            self._act_to_range_here.setEnabled(self._crt_timeline.can_to_range(self._crt_event, frame_id))
            self._act_to_ponctual_here.setEnabled(self._crt_timeline.can_to_ponctual(self._crt_event, frame_id))
            self._act_rem_crt_event.setEnabled(self._crt_event is not None)
            # from here to left
            if isinstance(self._crt_event, RangeEventModel) and (frame_id != self._crt_event.first):
                self._act_here_to_left.setToolTip("Goto Current Event's Start (Alt+Left)")
                self._here_to_left_target = self._crt_event.first
            else:
                self._act_here_to_left.setToolTip("Goto Previous Event's End (Alt+Left)")
                self._here_to_left_target = self._prv_event.last if self._prv_event else None
            self._act_here_to_left.setEnabled(self._here_to_left_target is not None)
            # from here to right
            if isinstance(self._crt_event, RangeEventModel) and (frame_id != self._crt_event.last):                            
                self._act_here_to_right.setToolTip("Goto Current Event's End (Alt+Right)")
                self._here_to_right_target = self._crt_event.last
            else:
                self._act_here_to_right.setToolTip("Goto Next Event's Start (Alt+Right)")
                self._here_to_right_target = self._nxt_event.first if self._nxt_event else None
            self._act_here_to_right.setEnabled(self._here_to_right_target is not None)       
            # event to here (move events boundaries)
            if isinstance(self._crt_event, RangeEventModel):
                self._act_left_to_here.setToolTip("Move Current Event's Start to here (Ctrl+Alt+Left)")
                self._left_to_here_target = self._crt_event.set_first \
                    if frame_id not in {self._crt_event.first, self._crt_event.last} \
                    else None
                self._act_right_to_here.setToolTip("Move Current Event's End to here (Ctrl+Alt+Right)")
                self._right_to_here_target = self._crt_event.set_last \
                    if frame_id not in {self._crt_event.first, self._crt_event.last} \
                    else None
            else:
                self._act_left_to_here.setToolTip("Move Previous Event's End to here (Ctrl+Alt+Left)")
                self._left_to_here_target = self._prv_event.set_last if self._prv_event else None
                self._act_right_to_here.setToolTip("Move Next Event's Start to here (Ctrl+Alt+Right)")
                self._right_to_here_target = self._nxt_event.set_first if self._nxt_event else None
            self._act_left_to_here.setEnabled(self._left_to_here_target is not None)
            self._act_right_to_here.setEnabled(self._right_to_here_target is not None)
                
        else:
            # No timeline selected
            self._act_timeline_rem.setEnabled(False)
            self._act_add_range_here.setEnabled(False)
            self._act_add_ponctual_here.setEnabled(False)
            self._act_to_range_here.setEnabled(False)
            self._act_to_ponctual_here.setEnabled(False)
            self._act_rem_crt_event.setEnabled(False)
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

    def onTimeLineListSelectedChanged(self, crt: TimeLineModel|None, prv: TimeLineModel|None):
        if self._time_window.playing: return
        self._set_crt_timeline(crt)
        self._reset_events()
        self._update_actions()

    def _update_events_n_actions(self, *_):
        if self._time_window.playing: return
        self._reset_events()
        self._update_actions()

    # ACTIONS
    # #######################################################################
    def onActTimelineRem(self, checked: bool):
        self._timeline_list.rem(self._crt_timeline)
        
    def onActAddRangeHere(self, checked: bool):
        self._crt_timeline.add_range(self._time_window.position)
        
    def onActAddPonctualHere(self, checked: bool):
        self._crt_timeline.add_ponctual(self._time_window.position)
    
    def onActToRangeHere(self, checked: bool):
        self._crt_timeline.to_range(self._crt_event, self._time_window.position)

    def onActToPonctualHere(self, checked: bool):
        self._crt_timeline.to_ponctual(self._crt_event, self._time_window.position)
        
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
