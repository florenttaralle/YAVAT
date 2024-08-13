import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QMouseEvent, QWheelEvent

class Graph(pg.PlotWidget):
    wheel_up        = pyqtSignal(QWheelEvent)
    wheel_down      = pyqtSignal(QWheelEvent)
    click           = pyqtSignal(float, QMouseEvent)

    def __init__(self, left: int, right: int, h: float):
        pg.PlotWidget.__init__(self)
        self.setMenuEnabled(False)
        self.setBackgroundBrush(Qt.white)
        self.showGrid(x = True, y = False, alpha = 0.5)
        self.showAxis('left', False)
        axBottom = self.getAxis('bottom')
        axBottom.setTickSpacing(1, 1) # (major, minor)
        self.hideButtons()
        line_pen    = pg.mkPen(color=(100, 100, 100), width=2)
        line        = pg.InfiniteLine(1, 0, pen=line_pen)
        self.addItem(line)
        self.setXRange(left, right)
        self.setYRange(0, h)

    def wheelEvent(self, event: QWheelEvent):
        angle = event.angleDelta()
        if (angle.x() != 0) and (angle.y() != 0): return
        if angle.y() != 0:
            if angle.y() > 0:   self.wheel_down.emit(event)
            else:               self.wheel_up.emit(event)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        pg.PlotWidget.mousePressEvent(self, event)
        if (not event.isAccepted()):
            frame_id = round(self.plotItem.vb.mapSceneToView(event.pos()).x())
            self.click.emit(frame_id, event)
