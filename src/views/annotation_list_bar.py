from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from typing import Callable
# ###########################################################
from src.models.annotation_list import AnnotationListModel, AnnotationModel
from src.models.time_window import TimeWindowModel
from src.models.timeline import TimelineModel, EventModel
from src.icons import Icons
from src.views.dialogs.annotation_editor import AnnotationEditorDialog
from src.views.dialogs.event_editor import EventEditorDialog
# ###########################################################

class AnnotationListBar(QToolBar):
    def __init__(self, time_window: TimeWindowModel|None=None, annotations: AnnotationListModel|None=None, parent: QWidget | None = None):
        QToolBar.__init__(self, parent)
        self.setMovable(False)
        self._annotations:              AnnotationListModel|None=None
        self._time_window:              TimeWindowModel|None=None
        self._crt_annotation:           AnnotationModel|None = None
        self._crt_event:                EventModel|None = None
        self._goto_left_target:         int|None = None
        self._goto_right_target:        int|None = None
        self._left_to_here_target:      Callable[[int]]|None = None
        self._right_to_here_target:     Callable[[int]]|None = None
        self._build_actions()        
        self.set_context(time_window, annotations)

    def set_context(self, time_window: TimeWindowModel|None, annotations: AnnotationListModel|None):
        if self._time_window is not None:
            self._time_window.position_changed.disconnect(self.onTimeWindowPositionChanged)
            self._time_window.playing_changed.disconnect(self.onTimeWindowPlayingChanged)
            self._annotations.selected_changed.disconnect(self.onAnnotationSelectedChanged)
            self._act_zoom_reset.triggered.disconnect(self._time_window.reset)
            self._act_zoom_in.triggered.disconnect(self._time_window.zoom_in)
            self._act_zoom_out.triggered.disconnect(self._time_window.zoom_out)
        self._time_window = time_window
        self._annotations = annotations
        if self._time_window is not None:
            self._time_window.position_changed.connect(self.onTimeWindowPositionChanged)
            self._time_window.playing_changed.connect(self.onTimeWindowPlayingChanged)
            self._annotations.selected_changed.connect(self.onAnnotationSelectedChanged)
            self._act_zoom_reset.triggered.connect(self._time_window.reset)
            self._act_zoom_in.triggered.connect(self._time_window.zoom_in)
            self._act_zoom_out.triggered.connect(self._time_window.zoom_out)
            self._set_crt_annotation(self._annotations.selected)
            self._update()
        else:
            self._set_crt_annotation(None)
            self.setEnabled(False)

    def _build_actions(self):
        # Annotations
        # - Create Annotation
        self._act_ano_create = QAction(Icons.TimelineAdd.icon(), "")
        self._act_ano_create.setToolTip("Add a new Timeline (T)")
        self._act_ano_create.setShortcut(Qt.Key.Key_T)
        self._act_ano_create.triggered.connect(self.onActTimelineAdd)
        self.addAction(self._act_ano_create)
        # - Edit Annotation
        self._act_ano_edit = QAction(Icons.Edit.icon(), "")
        self._act_ano_edit.setToolTip("Edit Current Annotation Properties")
        self._act_ano_edit.triggered.connect(self.onActAnnotationEdit)
        self.addAction(self._act_ano_edit)
        # - Delete Annotation
        self._act_ano_delete = QAction(Icons.TimelineRem.icon(), "")
        self._act_ano_delete.setToolTip("Delete Current Annotation")
        self._act_ano_delete.triggered.connect(self.onActAnnotationDelete)
        self.addAction(self._act_ano_delete)
        self.addSeparator()

        # View
        # - Reset Zoom
        self._act_zoom_reset = QAction(Icons.ZoomReset.icon(), "")
        self._act_zoom_reset.setToolTip("Reset Zoom")
        self.addAction(self._act_zoom_reset)
        # - Zoom In
        self._act_zoom_in = QAction(Icons.ZoomIn.icon(), "")
        self._act_zoom_in.setToolTip("Zoom In (+)")
        self._act_zoom_in.setShortcut(Qt.Key.Key_Plus)
        self.addAction(self._act_zoom_in)
        # - Zoom Out
        self._act_zoom_out = QAction(Icons.ZoomOut.icon(), "")
        self._act_zoom_out.setToolTip("Zoom Out (-)")
        self._act_zoom_out.setShortcut(Qt.Key.Key_Minus)
        self.addAction(self._act_zoom_out)
        self.addSeparator()
        
        # Event
        # - Create Event
        self._act_event_add = QAction(Icons.EventAdd.icon(), "")
        self._act_event_add.setToolTip("Add an Event here (E)")
        self._act_event_add.setShortcut(Qt.Key.Key_E)
        self._act_event_add.triggered.connect(self.onActEventCreate)
        self.addAction(self._act_event_add)
        # - Edit Event
        self._act_event_edit = QAction(Icons.EventInfo.icon(), "")
        self._act_event_edit.setToolTip("Edit Event (Ctrl + E)")
        self._act_event_edit.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_E))
        self._act_event_edit.triggered.connect(self.onActEventEdit)
        self.addAction(self._act_event_edit)
        # - Delete Event
        self._act_event_rem = QAction(Icons.EventRem.icon(), "")
        self._act_event_rem.setToolTip("Delete Event (Delete)")
        self._act_event_rem.setShortcut(Qt.Key.Key_Delete)
        self._act_event_rem.triggered.connect(self.onActEventDelete)
        self.addAction(self._act_event_rem)
        self.addSeparator()

        # - First To Here
        self._act_left_to_here = QAction(Icons.ArrowToRight.icon(), "")
        self._act_left_to_here.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Right))
        self._act_left_to_here.triggered.connect(self.onActLeftToHere)
        self.addAction(self._act_left_to_here)
        # - Last To Here
        self._act_right_to_here = QAction(Icons.ArrowToLeft.icon(), "")
        self._act_right_to_here.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Left))
        self._act_right_to_here.triggered.connect(self.onActRightToHere)
        self.addAction(self._act_right_to_here)
        self.addSeparator()

        # - Goto Left (Crt-First/Prv-Last)
        self._act_goto_left = QAction(Icons.ArrowFromRight.icon(), "")
        self._act_goto_left.setShortcut(QKeySequence(Qt.Modifier.SHIFT | Qt.Key.Key_Left))
        self._act_goto_left.triggered.connect(self.onGotoLeft)
        self.addAction(self._act_goto_left)
        # - Goto Right (Crt-Last/Nxt-First)
        self._act_goto_right = QAction(Icons.ArrowFromLeft.icon(), "")
        self._act_goto_right.setShortcut(QKeySequence(Qt.Modifier.SHIFT | Qt.Key.Key_Right))
        self._act_goto_right.triggered.connect(self.onGotoRight)
        self.addAction(self._act_goto_right)
        self.addSeparator()

    # Change Detection -> Update Actions
    # ################################################################
    def onTimeWindowPlayingChanged(self, playing: bool):
        self._update()

    def onAnnotationSelectedChanged(self, annotation: AnnotationModel|None):
        self._set_crt_annotation(annotation)
        self._update()

    def onTimeWindowPositionChanged(self, frame_id: int):
        self._update()

    def onEventAdded(self, event: EventModel):
        self._update()
    
    def onEventRemoved(self, event: EventModel):
        self._update()
    
    def onEventFirstChanged(self, first: int):
        self._update()
    
    def onEventLastChanged(self, last: int):
        self._update()
    # ################################################################

    # update internal statusses
    # ################################################################    
    def _set_crt_annotation(self, annotation: AnnotationModel|None) -> bool:
        if annotation != self._crt_annotation:
            if isinstance(self._crt_annotation, TimelineModel):
                self._crt_annotation.event_added.disconnect(self.onEventAdded)
                self._crt_annotation.event_removed.disconnect(self.onEventRemoved)
            self._crt_annotation = annotation
            if isinstance(self._crt_annotation, TimelineModel):
                self._crt_annotation.event_added.connect(self.onEventAdded)
                self._crt_annotation.event_removed.connect(self.onEventRemoved)
            return True
        else:
            return False
    
    def _set_crt_event(self, event: EventModel|None) -> bool:
        if event != self._crt_event:
            if self._crt_event is not None:
                self._crt_event.first_changed.disconnect(self.onEventFirstChanged)
                self._crt_event.last_changed.disconnect(self.onEventLastChanged)
            self._crt_event = event
            if self._crt_event is not None:
                self._crt_event.first_changed.connect(self.onEventFirstChanged)
                self._crt_event.last_changed.connect(self.onEventLastChanged)
            return True
        else:
            return False
    # ################################################################

    def _update(self):
        self.setEnabled(not self._time_window.playing)

        # alias for simpler code
        frame_id = self._time_window.position
        # update crt event
        if isinstance(self._crt_annotation, TimelineModel):
            self._set_crt_event(self._crt_annotation.at_frame_id(frame_id))
        else:
            self._set_crt_event(None)
        # update annotation action buttons
        self._act_ano_edit.setEnabled(self._crt_annotation is not None)
        self._act_ano_delete.setEnabled(self._crt_annotation is not None)
        if isinstance(self._crt_annotation, TimelineModel):
            # get prv & nxt events
            prv_event = self._crt_event.prv_event if self._crt_event is not None else self._crt_annotation.before_frame_id(frame_id)                
            nxt_event = self._crt_event.nxt_event if self._crt_event is not None else self._crt_annotation.after_frame_id(frame_id)
            # update Event action buttons
            self._act_event_add.setEnabled(self._crt_annotation.can_add(frame_id, frame_id))
            self._act_event_edit.setEnabled(self._crt_event is not None)
            self._act_event_rem.setEnabled(self._crt_event is not None)
            # update Event Left/Right to Here
            if self._crt_event is not None:
                # left = crt_event first
                self._act_left_to_here.setToolTip("Move Current Event's Start to here (Ctrl + Shit + Right)")
                self._left_to_here_target = self._crt_event.set_first if (frame_id != self._crt_event.first) else None
                # right = crt_event last
                self._act_right_to_here.setToolTip("Move Current Event's End to here (Ctrl + Shift + Left)")
                self._right_to_here_target = self._crt_event.set_last if (frame_id != self._crt_event.last) else None
            else:
                # left = prv_event last
                self._act_left_to_here.setToolTip("Move Previous Event's End to here (Ctrl + Shift + Right)")
                self._left_to_here_target = prv_event.set_last if prv_event else None
                # right = nxt_event first
                self._act_right_to_here.setToolTip("Move Next Event's Start to here (Ctrl + Shift + Left)")
                self._right_to_here_target = nxt_event.set_first if nxt_event else None
            self._act_left_to_here.setEnabled(self._left_to_here_target is not None)
            self._act_right_to_here.setEnabled(self._right_to_here_target is not None)
            # update Goto Left
            if (self._crt_event is not None) and (frame_id != self._crt_event.first):
                self._act_goto_left.setToolTip("Goto Current Event's Start (Shit + Left)")
                self._goto_left_target = self._crt_event.first
            elif prv_event is not None:
                self._act_goto_left.setToolTip("Goto Previous Event's End (Shift + Left)")
                self._goto_left_target = prv_event.last
            else:
                self._act_goto_left.setToolTip("Goto Video's Begining (Shift + Left)")
                self._goto_left_target = 0
            self._act_goto_left.setEnabled(True)
            # update Goto Right
            if (self._crt_event is not None) and (frame_id != self._crt_event.last):                            
                self._act_goto_right.setToolTip("Goto Current Event's End (Shift + Right)")
                self._goto_right_target = self._crt_event.last
            elif nxt_event is not None:
                self._act_goto_right.setToolTip("Goto Next Event's Start (Shift + Right)")
                self._goto_right_target = nxt_event.first
            else:
                self._act_goto_right.setToolTip("Goto Video's End (Shift + Right)")
                self._goto_right_target = self._time_window.duration - 1
            self._act_goto_right.setEnabled(True)   
        else:
            self._act_event_add.setEnabled(False)
            self._act_event_edit.setEnabled(False)
            self._act_event_rem.setEnabled(False)
            self._act_left_to_here.setEnabled(False)
            self._act_right_to_here.setEnabled(False)
            self._act_goto_left.setEnabled(False)
            self._act_goto_right.setEnabled(False)
    # ################################################################


    # Action Implementations
    # ################################################################
    def onActTimelineAdd(self):
        timeline = TimelineModel(self._time_window.duration, selected=True)
        if self.onActAnnotationEdit(timeline):
            self._annotations.append(timeline)
    
    def onActAnnotationEdit(self, annotation: AnnotationModel|None=None) -> bool:
        if annotation is None:
            annotation = self._crt_annotation
        return AnnotationEditorDialog().exec(annotation)
    
    def onActAnnotationDelete(self):
        button = QMessageBox.warning(None, 
                                     "Delete Annotation", 
                                     f"About to delete annotation: '{self._crt_annotation.name}'", 
                                     QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel, 
                                     QMessageBox.StandardButton.Cancel)
        if button == QMessageBox.StandardButton.Ok:
            self._annotations.remove(self._crt_annotation)

    def onActEventCreate(self):
        frame_id = self._time_window.position
        event = EventModel(frame_id, frame_id)
        self._crt_annotation.add(event)

    def onActEventEdit(self):
        EventEditorDialog().exec(self._crt_event)
    
    def onActEventDelete(self):
        self._crt_event.remove()
    
    def onActLeftToHere(self):      self._left_to_here_target(self._time_window.position)
    def onActRightToHere(self):     self._right_to_here_target(self._time_window.position)
    def onGotoLeft(self):           self._time_window.goto(self._goto_left_target)
    def onGotoRight(self):          self._time_window.goto(self._goto_right_target)
    # ################################################################
