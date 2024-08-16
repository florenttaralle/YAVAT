import pyqtgraph as pg
from typing import List
from PyQt6.QtCore import pyqtSignal, QPointF, QPoint, QTime
from PyQt6.QtGui import QMouseEvent, QWheelEvent, QContextMenuEvent, QColorConstants, QPen
from PyQt6.QtWidgets import QGraphicsView

class Graph(pg.PlotWidget):
    wheel_up        = pyqtSignal(QWheelEvent)
    wheel_down      = pyqtSignal(QWheelEvent)
    click           = pyqtSignal(float, QMouseEvent)
    context_menu    = pyqtSignal(float, QContextMenuEvent)
    
    def __init__(self, left: int, position: int, right: int, h: float, fps: float):
        pg.PlotWidget.__init__(self)
        self.setMenuEnabled(False)
        self.enableMouse
        self.setBackgroundBrush(QColorConstants.Transparent)

        axBottom = self.getAxis('bottom')
        axBottom.setStyle(showValues=False)
        axBottom.setTickSpacing(fps, 1)
        self.showAxis('left', False)
        self.hideButtons()
        self.showGrid(x=True, y=False, alpha=1.)

        line_pen    = QPen(QColorConstants.Gray)
        line_pen.setCosmetic(True)
        line_pen.setWidth(2)
        line        = pg.InfiniteLine(h/2, 0, pen=line_pen)
        self.addItem(line)

        line_pen    = QPen(QColorConstants.Red)
        line_pen.setCosmetic(True)
        line_pen.setWidth(2)
        self.position_line = pg.InfiniteLine(0, 90, pen=line_pen)
        self.position_line.setVisible(False)
        self.addItem(self.position_line)

        line_pen    = QPen(QColorConstants.Gray)
        line_pen.setCosmetic(True)
        line_pen.setWidth(2)
        self.hovered_line = pg.InfiniteLine(0, 90, pen=line_pen)
        self.hovered_line.setVisible(False)
        self.addItem(self.hovered_line)
        
        self.setYRange(0, h)
        self.set_time_window(left, position, right)

    def set_time_window(self, left: int, position: int, right: int):
        self.setXRange(left, right, padding=0)
        if left <= position <= right:
            self.position_line.setVisible(True)
            self.position_line.setX(position)
        else:
            self.position_line.setVisible(False)

    def enterEvent(self, event):
        self.hovered_line.setVisible(True)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        frame_id = self._frame_id(event.pos())
        self.hovered_line.setX(frame_id)
    
    def leaveEvent(self, event):
        self.hovered_line.setVisible(False)

    def wheelEvent(self, event: QWheelEvent):
        angle = event.angleDelta()
        if (angle.x() != 0) and (angle.y() != 0): return
        if angle.y() != 0:
            if angle.y() > 0:   self.wheel_down.emit(event)
            else:               self.wheel_up.emit(event)
        event.accept()

    def _frame_id(self, point: QPointF | QPoint) -> int:
        if isinstance(point, QPoint):
            point = QPointF(point)
        frame_id = round(self.plotItem.vb.mapSceneToView(point).x())
        return frame_id 

    def mousePressEvent(self, event: QMouseEvent):
        QGraphicsView.mousePressEvent(self, event)
        if event.isAccepted(): return
        frame_id = self._frame_id(event.pos())
        self.click.emit(frame_id, event)
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        pg.PlotWidget.contextMenuEvent(self, event)
        if event.isAccepted(): return
        frame_id = self._frame_id(event.pos())
        self.context_menu.emit(frame_id, event)
        event.accept()
