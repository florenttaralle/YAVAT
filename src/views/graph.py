from PyQt6.QtCore import Qt, QPoint, QPointF, pyqtSignal, QRectF
from PyQt6.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsView
from PyQt6.QtGui import QColorConstants, QPen, QMouseEvent, QContextMenuEvent, QWheelEvent
import pyqtgraph as pg
from src.models.time_window import TimeWindowModel


class GraphView(pg.PlotWidget):
    context_menu    = pyqtSignal(int, QContextMenuEvent)
    "SIGNAL: context_menu(frame_id: int, event: QContextMenuEvent)"
    click           = pyqtSignal(int, QMouseEvent)
    "SIGNAL: click(frame_id: int, event: QMouseEvent)"
    double_click    = pyqtSignal(int, QMouseEvent)
    "SIGNAL: double_click(frame_id: int, event: QMouseEvent)"
    
    WHEEL_MOVE_DURATION_PRC = 0.01
    
    def __init__(self, time_window: TimeWindowModel, parent: QWidget|None=None):
        pg.PlotWidget.__init__(self, parent)
        self._time_window   = time_window
        self.setMenuEnabled(False)
        self.setMouseEnabled(x=False, y=False)
        self.hideButtons()
        
        self.setBackgroundBrush(QColorConstants.Transparent)
        self.showAxis('left', False)
        self.showAxis('bottom', False)

        # add the time position line
        self._position_line = QGraphicsLineItem(0, 0, 0, 1)
        pen = QPen(QColorConstants.Red)
        pen.setCosmetic(True)
        pen.setWidth(3)
        self._position_line.setPen(pen)
        self._position_line.setZValue(10)
        self.addItem(self._position_line)

        time_window.window_changed.connect(self.onTimeWindowChanged)
        self.onTimeWindowChanged(time_window.left, time_window.position, time_window.right)

    def setYRange(self, ymin: float, ymax: float, padding: float=0.01):
        self._position_line.setLine(self._time_window.position, ymin, self._time_window.position, ymax)
        pg.ViewBox.setYRange(self, ymin, ymax, padding)

    def onTimeWindowChanged(self, left: int, position: int, right: int):
        self._position_line.setX(position)
        pg.ViewBox.setXRange(self, left, right, 0.01)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        QGraphicsView.mouseDoubleClickEvent(self, event)
        if event.isAccepted(): return
        frame_id = self._frame_id(event.pos())
        self.double_click.emit(frame_id, event)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        QGraphicsView.mousePressEvent(self, event)
        if event.isAccepted(): return
        if event.button() == Qt.MouseButton.LeftButton:
            frame_id = self._frame_id(event.pos())
            self._time_window.goto(frame_id)
            self.click.emit(frame_id, event)
        else:
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
                # Vertical
                if angle.y() > 0:   
                    # wheel down
                    self._time_window.zoom_in()
                else:
                    # wheel up
                    self._time_window.zoom_out()
                # Horizaontal
            else:
                if angle.x() > 0:
                    # wheel right
                    move_n_frames = int(self._time_window.duration * self.WHEEL_MOVE_DURATION_PRC)                    
                    self._time_window.move(move_n_frames)
                else:
                    # wheel left
                    move_n_frames = int(self._time_window.duration * self.WHEEL_MOVE_DURATION_PRC)
                    self._time_window.move(-move_n_frames)
                
        event.accept()

    def _frame_id(self, point: QPointF | QPoint) -> int:
        if isinstance(point, QPoint):
            point = QPointF(point)
        frame_id = round(self.plotItem.vb.mapSceneToView(point).x())
        return frame_id 
