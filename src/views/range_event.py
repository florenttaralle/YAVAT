from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent
from PyQt6.QtGui import QPen, QBrush, QPainter, QPainterPath
from enum import Enum, auto

from .event import EventView
from .color_specifications import RangeEventColorSpecification
from src.models.range_event import RangeEventModel, EventModel

class Action(Enum):
    NoAction            = 0
    Hovering            = auto()
    HoveringLeftHandle  = auto()
    HoveringRightHandle = auto()
    Moving              = auto()
    MovingLeftHandle    = auto()
    MovingRightHandle   = auto()
    
    def isHovering(self):
        return self in {Action.Hovering, Action.HoveringLeftHandle, Action.HoveringRightHandle}
    def isMoving(self):
        return self in {Action.Moving, Action.MovingLeftHandle, Action.MovingRightHandle}
    def isHandleMoving(self):
        return self in {Action.MovingLeftHandle, Action.MovingRightHandle}
    def isActive(self):
        return self != Action.NoAction

    
class RangeEventView(EventView):
    def __init__(self, 
            model: RangeEventModel,
            y: float, h: float, handleWidth: float=.1, cornerRadius: float=.1,
            colors: RangeEventColorSpecification|None = None, parent: QGraphicsItem|None=None):
        self._handleWidth       = handleWidth
        self._corner_radius     = cornerRadius
        self._colors:           RangeEventColorSpecification = colors if colors else RangeEventColorSpecification()
        self._action:           Action = Action.NoAction
        self._pressX:           float | None = None
        EventView.__init__(self, model, y, h, parent)
        self._model.first_changed.connect(self.onModelFirstChanged)
        self._model.last_changed.connect(self.onModelLastChanged)
        
    def _leftHandleX0(self):    return self._model.first - self._handleWidth / 2
    def _leftHandleX1(self):    return self._model.first + self._handleWidth / 2
    def _rightHandleX0(self):   return self._model.last - self._handleWidth / 2
    def _rightHandleX1(self):   return self._model.last + self._handleWidth / 2
    def _y0(self):              return self._y - self._h / 2

    def _update_geometry(self):
        self.prepareGeometryChange()
        width = self._model.last - self._model.first + self._handleWidth
        self._rect = QRectF(self._leftHandleX0(), self._y0(), width, self._h)

    def _update_tooltip(self):
        tooltip = self._model.label + " " if self._model.label else ""
        tooltip = f"{tooltip}@ [{self._model.first};{self._model.last}]"
        self.setToolTip(tooltip)

    def onModelFirstChanged(self, frame_id: int):
        self._update_geometry()
        self._update_tooltip()
        self.update()

    def onModelLastChanged(self, frame_id: int):
        self._update_geometry()
        self._update_tooltip()
        self.update()

    def _set_action(self, value: Action):
        if value != self._action:
            self._action = value
            match value:
                case Action.NoAction | Action.Hovering :
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
                case Action.HoveringLeftHandle | Action.HoveringRightHandle:   
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                case Action.Moving:
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                case Action.MovingLeftHandle | Action.MovingRightHandle:
                    self.setCursor(Qt.CursorShape.SplitHCursor)
            self.update()

    def _check_hover_handle(self, pos: QPointF):
        if (pos.x() < self._leftHandleX0()) or (pos.x() > self._rightHandleX1()):
            self._set_action(Action.NoAction)
        elif pos.x() <= self._leftHandleX1():
            self._set_action(Action.HoveringLeftHandle)
        elif pos.x() >= self._rightHandleX0():
            self._set_action(Action.HoveringRightHandle)
        else:
            self._set_action(Action.Hovering)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        self._check_hover_handle(event.pos())

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent):
        self._check_hover_handle(event.pos())

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        self._set_action(Action.NoAction)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        match event.button():
            case Qt.MouseButton.LeftButton:
                self._pressX = event.pos().x()
                match self._action:
                    case Action.Hovering:
                        self._set_action(Action.Moving)
                    case Action.HoveringLeftHandle:
                        self._set_action(Action.MovingLeftHandle)
                    case Action.HoveringRightHandle:
                        self._set_action(Action.MovingRightHandle)
                event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        match self._action:
            case Action.Moving:
                offsetX     = event.pos().x() - self._pressX
                closestX0   = round(self._model.first + offsetX)
                closestX1   = round(self._model.last + offsetX)
                if (closestX0 >= self._leftLimit()) and (closestX1 <= self._rightLimit()) and (closestX0 != self._model.first):
                    self._pressX        += closestX0 - self._model.first
                    self._model.first   = closestX0
                    self._model.last    = closestX1
            
            case Action.MovingLeftHandle:
                closestFrameId = round(event.pos().x())
                if (closestFrameId >= self._leftLimit()) and (closestFrameId < self._model.last):
                    self._model.first = closestFrameId

            case Action.MovingRightHandle:
                closestFrameId = round(event.pos().x())
                if (closestFrameId <= self._rightLimit()) and (closestFrameId > self._model.first):
                    self._model.last = closestFrameId

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        self._check_hover_handle(event.pos())

    def paint(self, painter: QPainter, *args):
        path    = QPainterPath()
        path.addRoundedRect(self._rect, self._corner_radius, self._corner_radius, Qt.SizeMode.AbsoluteSize)
        # fill content
        brush = self._obj_brush()
        painter.fillPath(path, brush)
        # draw handles
        self.paint_left_handle(painter, path)
        self.paint_right_handle(painter, path)
        # draw border
        pen = self._obj_pen()
        painter.setPen(pen)
        painter.drawPath(path)

    def _obj_pen(self) -> QPen:
        pen = QPen(self._colors.border)
        pen.setWidth(2)
        pen.setCosmetic(True)
        return pen
    
    def _obj_brush(self) -> QBrush:
        if self._action.isHovering() | self._action.isHandleMoving():           
                                                color = self._colors.object_hovering
        elif self._action == Action.Moving:     color = self._colors.object_moving
        else:                                   color = self._colors.object_default
        return QBrush(color)

    def _left_handle_brush(self) -> QBrush:
        if self._action == Action.HoveringLeftHandle:   color = self._colors.handle_right_hovering
        elif self._action == Action.MovingLeftHandle:   color = self._colors.handle_right_moving
        else:                                           color = self._colors.handle_right_default
        return QBrush(color)

    def _right_handle_brush(self) -> QBrush:
        if self._action == Action.HoveringRightHandle:  color = self._colors.handle_left_hovering
        elif self._action == Action.MovingRightHandle:  color = self._colors.handle_left_moving
        else:                                           color = self._colors.handle_left_default
        return QBrush(color)
    
    def paint_left_handle(self, painter: QPainter, facePath: QPainterPath):
        mask_rect   = QRectF(self._leftHandleX0(), self._y0(), self._handleWidth, self._h)
        mask        = QPainterPath()
        mask.addRect(mask_rect)
        path        = facePath.intersected(mask)
        painter.fillPath(path, self._left_handle_brush())

    def paint_right_handle(self, painter: QPainter, facePath: QPainterPath):
        mask_rect   = QRectF(self._rightHandleX0(), self._y0(), self._handleWidth, self._h)
        mask        = QPainterPath()
        mask.addRect(mask_rect)
        path        = facePath.intersected(mask)
        painter.fillPath(path, self._right_handle_brush())
