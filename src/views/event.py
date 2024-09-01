from __future__ import annotations
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import QGraphicsSceneMouseEvent
from src.models.event import EventModel
from enum import Enum, auto
from src.views.dialogs.event_editor import EventEditorDialog

class EventViewState(Enum):
    Outside         = auto()
    OverBody        = auto()
    OverLeftHdl     = auto()
    OverRightHdl    = auto()
    MovingBody      = auto()
    MovingLeftHdl   = auto()
    MovingRightHdl  = auto()

class EventView(QGraphicsObject):
    ADD_W: float = .2
    HDL_W: float = .2
    
    left_click = pyqtSignal(object, int)
    "SIGNAL: left_click(event: EventView, frame_id: int)"
    
    def __init__(self, event: EventModel, color: QColor, parent: QGraphicsItem|None=None):
        QGraphicsObject.__init__(self, parent)
        self._event = event
        self._color = QColor(color)
        # required re-paint on hover in/out
        self.setAcceptHoverEvents(True)
        # set focusable to allow receiving keyPress/Release events
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self._outer_rect:       QRectF = None
        self._inner_rect:       QRectF = None
        self._lhdl_rect:        QRectF = None
        self._rhdl_rect:        QRectF = None
        self._lhdl_line:        QLineF = None
        self._rhdl_line:        QLineF = None
        self._update_geometry()
        self._hdl_hidden        = False
        self._on_left_handle    = False
        self._on_right_handle   = False
        self._state             = EventViewState.Outside
        self._press_x:          int = None
        event.first_changed.connect(self.onEventFirstChanged)
        event.last_changed.connect(self.onEventLastChanged)

    def set_color(self, color: QColor):
        self._color = color
        self.update()

    def _update_geometry(self):
        self.prepareGeometryChange()
        x0_                 = self._event.first - self.ADD_W
        x1_                 = self._event.last + self.ADD_W
        hdl_w               = min(2 * (self.HDL_W + self.ADD_W), (x1_ - x0_ + 2 * self.HDL_W) / 2)
        self._outer_rect    = QRectF(x0_ - self.HDL_W, 0, x1_ - x0_ + 2 * self.HDL_W, 1)
        self._inner_rect    = QRectF(x0_, .1, x1_ - x0_, .8)
        self._lhdl_rect     = QRectF(x0_ - self.HDL_W, 0, hdl_w, 1)
        self._rhdl_rect     = QRectF(x1_ - self.HDL_W, 0, hdl_w, 1)
        self._lhdl_line     = QLineF(x0_, .1, x0_, .9)
        self._rhdl_line     = QLineF(x1_, .1, x1_, .9)
    
    def boundingRect(self) -> QRectF:
        return self._outer_rect

    @property
    def color(self) -> QColor:
        return self._color
    @color.setter
    def color(self, color: QColor):
        if color != self._color:
            self._color = color
            self.update()

    def _set_state(self, state: EventViewState):
        if state == self._state: return
        self._state = state
        match state:
            case EventViewState.Outside | EventViewState.OverBody:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            case EventViewState.MovingBody:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            case EventViewState.OverLeftHdl | EventViewState.OverRightHdl:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            case EventViewState.MovingLeftHdl | EventViewState.MovingRightHdl:
                self.setCursor(Qt.CursorShape.SplitHCursor)
        self.update()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        QGraphicsObject.hoverEnterEvent(self, event)
        # required for keyPressEvent
        self.setFocus(Qt.FocusReason.NoFocusReason)
        self._set_hdl_hidden(event.modifiers() == Qt.KeyboardModifier.ControlModifier)
        if self._set_on_left_handle(event.pos()):
            self._set_state(EventViewState.OverLeftHdl)
        elif self._set_on_right_handle(event.pos()):
            self._set_state(EventViewState.OverRightHdl)
        else:
            self._set_state(EventViewState.OverBody)
    
    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        QGraphicsObject.hoverLeaveEvent(self, event)
        # required for keyPressEvent
        self.clearFocus()
        self._set_state(EventViewState.Outside)

    def _set_on_left_handle(self, pos: QPointF) -> bool:
        self._on_left_handle = self._lhdl_rect.contains(pos)
        return self._on_left_handle

    def _set_on_right_handle(self, pos: QPointF) -> bool:
        self._on_right_handle = self._rhdl_rect.contains(pos)
        return self._on_right_handle
    
    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent):
        if not self._hdl_hidden:
            if self._set_on_left_handle(event.pos()):
                self._set_state(EventViewState.OverLeftHdl)
            elif self._set_on_right_handle(event.pos()) :
                self._set_state(EventViewState.OverRightHdl)
            else:
                self._set_state(EventViewState.OverBody)
        else:
            self._set_state(EventViewState.OverBody)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        # ignore double clicks
        if (event.type() == QEvent.Type.GraphicsSceneMouseDoubleClick):
            QGraphicsObject.mousePressEvent(self, event)
        # manage only left clicks
        elif event.button() != Qt.MouseButton.LeftButton: 
            QGraphicsObject.mousePressEvent(self, event)
        # ignore click if shift pressed
        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            QGraphicsObject.mousePressEvent(self, event)
            self.left_click.emit(self, round(event.pos().x()))
        else:
            # manage depending on state
            self._press_x = event.pos().x()
            match self._state:
                case EventViewState.OverBody:
                    self._set_state(EventViewState.MovingBody)
                case EventViewState.OverLeftHdl:
                    self._set_state(EventViewState.MovingLeftHdl)
                case EventViewState.OverRightHdl:
                    self._set_state(EventViewState.MovingRightHdl)
            self.left_click.emit(self, round(event.pos().x()))


    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        # when mouse pressed (moving)
        match self._state:
            case EventViewState.MovingBody:
                offsetX     = event.pos().x() - self._press_x
                closestX0   = round(self._event.first + offsetX)
                closestX1   = round(self._event.last + offsetX)
                if (closestX0 >= self._event.first_min) and (closestX1 <= self._event.last_max) and (closestX0 != self._event.first):
                    self._press_x += closestX0 - self._event.first
                    self._event.set_first(closestX0)
                    self._event.set_last(closestX1)

            case EventViewState.MovingLeftHdl:
                closestFrameId = round(event.pos().x())
                if (closestFrameId >= self._event.first_min) and (closestFrameId <= self._event.first_max):
                    self._event.set_first(closestFrameId)
            
            case EventViewState.MovingRightHdl:
                closestFrameId = round(event.pos().x())
                if (closestFrameId >= self._event.last_min) and (closestFrameId <= self._event.last_max):
                    self._event.set_last(closestFrameId)
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        match self._state:
            case EventViewState.MovingBody:
                self._set_state(EventViewState.OverBody)
            case EventViewState.MovingLeftHdl:
                self._set_state(EventViewState.OverLeftHdl)
            case EventViewState.MovingRightHdl:
                self._set_state(EventViewState.OverRightHdl)

    # def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
    #     QGraphicsObject.mouseDoubleClickEvent(self, event)
    #     if event.isAccepted(): return
    #     EventEditorDialog().exec(self._event)
    #     event.accept()

    def _set_hdl_hidden(self, hdl_hidden: bool):
        if hdl_hidden != self._hdl_hidden:
            self._hdl_hidden = hdl_hidden
            if hdl_hidden:
                self._set_state(EventViewState.OverBody)
            elif self._on_left_handle:
                self._set_state(EventViewState.OverLeftHdl)
            elif self._on_right_handle:
                self._set_state(EventViewState.OverRightHdl)
            else:
                self._set_state(EventViewState.OverBody)
            self.update()

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        QGraphicsObject.keyPressEvent(self, event)
        # hide handles if control key is pressed when hovering
        self._set_hdl_hidden(event.modifiers() == Qt.KeyboardModifier.ControlModifier)

    def keyReleaseEvent(self, event: QKeyEvent | None):
        QGraphicsObject.keyReleaseEvent(self, event)
        # hide handles if control key is pressed when hovering
        self._set_hdl_hidden(event.modifiers() == Qt.KeyboardModifier.ControlModifier)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget|None=None):
        need_handles = self._state not in {EventViewState.Outside, EventViewState.MovingBody}
        if need_handles and not self._hdl_hidden:
            # Left Handle
            pen = QPen(QColorConstants.Black)
            match self._state:
                case EventViewState.MovingLeftHdl:  pen.setWidth(10)
                case EventViewState.OverLeftHdl:    pen.setWidth(12)
                case _:                             pen.setWidth(10)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawLine(self._lhdl_line)
            # Right Handle
            pen = QPen(QColorConstants.Black)
            match self._state:
                case EventViewState.MovingRightHdl: pen.setWidth(10)
                case EventViewState.OverRightHdl:   pen.setWidth(12)
                case _:                             pen.setWidth(10)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawLine(self._rhdl_line)
        # draw central part on top
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color)
        painter.drawRect(self._inner_rect)

    def onEventFirstChanged(self, frame_id: int):
        self._update_geometry()
        self.update()

    def onEventLastChanged(self, frame_id: int):
        self._update_geometry()
        self.update()
