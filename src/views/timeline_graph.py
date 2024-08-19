from PyQt6.QtCore import Qt, QPoint, QPointF, pyqtSignal
from PyQt6.QtWidgets import QWidget, QGraphicsRectItem, QGraphicsLineItem, QGraphicsView
from PyQt6.QtGui import QColor, QColorConstants, QPen, QMouseEvent, QContextMenuEvent, QWheelEvent
import pyqtgraph as pg
from src.models.time_window import TimeWindowModel


class TimelineGraphView(pg.PlotWidget):
    context_menu = pyqtSignal(int, QContextMenuEvent)
    "SIGNAL: context_menu(frame_id: int, event: QContextMenuEvent)"
    
    def __init__(self, time_window: TimeWindowModel, color: QColor, parent: QWidget|None=None):
        pg.PlotWidget.__init__(self, parent)
        self._time_window   = time_window
        self.setMenuEnabled(False)
        self.setBackgroundBrush(QColorConstants.Transparent)
        self.showAxis('left', False)
        self.showAxis('bottom', False)
        self.hideButtons()
        self.setXRange(time_window.left, time_window.right, 0.01)
        time_window.window_changed.connect(self._update_time_window)
        self.setYRange(0, 1, .05)

        # add the border
        self._border = QGraphicsRectItem(0, .1, time_window.duration-1, .8)
        self._border.setBrush(QColorConstants.Transparent)
        pen = QPen(color)
        pen.setWidth(4)
        pen.setCosmetic(True)
        self._border.setPen(pen)
        self._border.setOpacity(.6)
        self.addItem(self._border)

        # add the time position line
        self._position_line = QGraphicsLineItem(time_window.position, 0, time_window.position, 1)
        pen = QPen(QColorConstants.Red)
        pen.setCosmetic(True)
        pen.setWidth(3)
        self._position_line.setPen(pen)
        self._position_line.setZValue(1)
        self.addItem(self._position_line)

    @property
    def color(self) -> QColor:
        return self._border.pen().color()
    @color.setter
    def color(self, color: QColor):
        self._border.pen().setColor(color)

    def _update_time_window(self, left: int, position: int, right: int):
        self.setXRange(left, right, .01)
        self._position_line.setLine(position, 0, position, 1)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            frame_id = self._frame_id(event.pos())
            self._time_window.goto(frame_id)
        event.accept()

    def contextMenuEvent(self, event: QContextMenuEvent):
        QGraphicsView.contextMenuEvent(self, event)
        if event.isAccepted(): return
        frame_id = self._frame_id(event.pos())
        self.context_menu.emit(frame_id, event)
        event.accept()
    
    def wheelEvent(self, event: QWheelEvent):
        ctrl_pressed = (event.modifiers() == Qt.KeyboardModifier.ControlModifier)
        angle = event.angleDelta()
        if ctrl_pressed and ((angle.x() == 0) or (angle.y() == 0)):
            if angle.y() != 0:
                if angle.y() > 0:   
                    # wheel down
                    self._time_window.zoom_in()
                else:
                    # wheel up
                    self._time_window.zoom_out()
        event.accept()

    def _frame_id(self, point: QPointF | QPoint) -> int:
        if isinstance(point, QPoint):
            point = QPointF(point)
        frame_id = round(self.plotItem.vb.mapSceneToView(point).x())
        return frame_id 
