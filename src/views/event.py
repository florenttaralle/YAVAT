from PyQt6.QtCore import pyqtSignal, QRectF
from PyQt6.QtWidgets import QGraphicsObject, QGraphicsItem, QGraphicsSceneMouseEvent
from src.models.event import EventModel

class EventView(QGraphicsObject):
    double_click    = pyqtSignal(object, int, QGraphicsSceneMouseEvent)
    
    def __init__(self, model: EventModel, y:float, h: float, parent: QGraphicsItem|None=None):
        QGraphicsObject.__init__(self, parent)
        self._model     = model
        self._y         = y
        self._h         = h
        self._rect:     QRectF = None
        self.setAcceptHoverEvents(True)
        # self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setSelected(True)
        self._update_geometry()
        self._update_tooltip()
    
    def boundingRect(self) -> QRectF:
        return self._rect

    @property
    def model(self) -> EventModel:
        return self._model
    
    def _update_geometry(self):
        raise NotImplementedError()
    
    def _update_tooltip(self):
        raise NotImplementedError()
    
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

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        QGraphicsObject.mouseDoubleClickEvent(self, event)
        closestFrameId = round(event.pos().x())
        self.double_click.emit(self, closestFrameId, event)

