from PyQt5.QtCore import pyqtSignal, QRectF, Qt
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsObject, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent
from PyQt5.QtGui import QPen, QBrush, QPainter, QPainterPath
from enum import Enum, auto
from .color_specifications import EventColorSpecification
from src.models.ponctual_event import PonctualEventModel, EventModel

class Action(Enum):
    NoAction            = 0
    Hovering            = auto()
    Moving              = auto()
    
class PonctualEventView(QGraphicsObject):
    double_click = pyqtSignal(object, int, QGraphicsSceneMouseEvent)
    right_click  = pyqtSignal(object, int, QGraphicsSceneMouseEvent)
    
    def __init__(self, 
            model: PonctualEventModel,
            y: float, h: float, width: float=.4, cornerRadius: float=.1,
            colors: EventColorSpecification|None = None, 
            parent: QGraphicsItem|None=None):
        
        QGraphicsObject.__init__(self, parent)
        self._model             = model
        self._y                 = y
        self._h                 = h
        self._w                 = width
        self._corner_radius     = cornerRadius
        self._colors:           EventColorSpecification = colors if colors else EventColorSpecification()
        self._rect:             QRectF = None
        self._action:           Action = Action.NoAction
        self._pressX:           float | None = None
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setSelected(True)
        self._update_geometry()
        self._update_tooltip()
        self._model.frame_id_changed.connect(self.onModelFrameIdChanged)
        self._model.prv_event_changed.connect(self.onPrvEventChanged)
        self._model.prv_event_changed.connect(self.onNxtEventChanged)

    def _x0(self):  return self._model.frame_id - self._w / 2
    def _x1(self):  return self._model.frame_id + self._w / 2
    def _y0(self):  return self._y - self._h / 2

    def _update_geometry(self):
        self.prepareGeometryChange()
        self._rect = QRectF(self._x0(), self._y0(), self._w, self._h)

    def _update_tooltip(self):
        tooltip = self._model.label + " " if self._model.label else ""
        tooltip = f"{tooltip}@ {self._model.frame_id}"
        self.setToolTip(tooltip)
            
    def onModelFrameIdChanged(self, frame_id: int):
        self._update_geometry()
        self._update_tooltip
        self.update()

    def onPrvEventChanged(self, event: EventModel|int):
        pass

    def onNxtEventChanged(self, event: EventModel|int):
        pass

    def _leftLimit(self) -> int:
        if isinstance(self._model.prv_event, EventModel):
            return self._model.prv_event.last + 1
        else:
            return self._model.prv_event
    
    def _rightLimit(self) -> int:
        if isinstance(self._model.nxt_event, EventModel):
            return self._model.nxt_event.first - 1
        else:
            return self._model.nxt_event
    
    def _set_action(self, value: Action):
        if value != self._action:
            self._action = value
            match value:
                case Action.NoAction | Action.Hovering :
                    self.setCursor(Qt.OpenHandCursor)
                case Action.Moving:
                    self.setCursor(Qt.ClosedHandCursor)
            self.update()

    def boundingRect(self) -> QRectF:
        return self._rect

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        self._set_action(Action.Hovering)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        self._set_action(Action.NoAction)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        match event.button():
            case Qt.MouseButton.LeftButton:
                self._set_action(Action.Moving)
                self._pressX = event.pos().x()
            case Qt.MouseButton.RightButton:
                closestFrameId = round(event.pos().x())
                self.right_click.emit(self, closestFrameId, event)
        
    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        closestFrameId = round(event.pos().x())
        self.double_click.emit(self, closestFrameId, event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self._action == Action.Moving:
            offsetX         = event.pos().x() - self._pressX
            closestFrameId  = round(self._model.frame_id + offsetX)
            if (closestFrameId >= self._leftLimit()) and (closestFrameId <= self._rightLimit()) and (closestFrameId != self._model.frame_id):
                self._pressX    += closestFrameId - self._model.frame_id
                self._model.frame_id = closestFrameId

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        self._set_action(Action.Hovering)

    def paint(self, painter: QPainter, *args):
        path    = QPainterPath()
        path.addRoundedRect(self._rect, self._corner_radius, self._corner_radius, Qt.SizeMode.AbsoluteSize)
        # fill content
        brush = self._obj_brush()
        painter.fillPath(path, brush)
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
        if self._action == Action.Hovering:     color = self._colors.object_hovering
        elif self._action == Action.Moving:     color = self._colors.object_moving
        else:                                   color = self._colors.object_default
        return QBrush(color)
