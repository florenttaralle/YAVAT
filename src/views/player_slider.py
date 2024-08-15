from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QSlider, QStyle, QStyleOptionSlider
from src.models.video_file import VideoFile

class PlayerSlider(QSlider):
    STYLESHEET = """
        QSlider::groove:horizontal {
            height: 5px;
            border: 0px;
            margin: 0px;
            position: absolute;
        }
        
        QSlider::handle:horizontal {
            background: #8a88fc;
            width: 5px;
            margin: 0px 0px;
        }

        QSlider::add-page:horizontal {
            background: black;
        }
        
        QSlider::sub-page:horizontal {
            background: #6563ff;
        }        
    """
    
    def __init__(self, video_file: VideoFile, parent: QWidget|None=None):
        QSlider.__init__(self, Qt.Orientation.Horizontal, parent)
        self._video_file = video_file
        self.setStyleSheet(self.STYLESHEET)
        video_file.ready_changed.connect(self.onVideoFileReadyChanged)
        video_file.frame_id_changed.connect(self.setValue)
        self.sliderMoved.connect(lambda: self._video_file.gotoFrameId(self.value()))
        self.setFixedHeight(5)

    def onVideoFileReadyChanged(self, ready: bool):
        self.setEnabled(self._video_file.valid)
        if self._video_file.valid:
            self.setMaximum(self._video_file.n_frames - 1)
            self.setValue(self._video_file.frame_id)

    def mousePressEvent(self, event):
        QSlider.mousePressEvent(self, event)
        if event.button() == Qt.MouseButton.LeftButton:
            frame_id = self.pixelPosToRangeValue(event.pos())
            self._video_file.gotoFrameId(frame_id)
        
    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self)

        if self.orientation() == Qt.Orientation.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1;
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Orientation.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                               sliderMax - sliderMin, opt.upsideDown)
