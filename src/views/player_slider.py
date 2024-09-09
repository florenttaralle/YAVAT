from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QSlider, QStyle, QStyleOptionSlider
from src.models.video import VideoModel

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
    
    def __init__(self, video: VideoModel|None=None, parent: QWidget|None=None):
        QSlider.__init__(self, Qt.Orientation.Horizontal, parent)
        self._video: VideoModel|None = None
        self.setStyleSheet(self.STYLESHEET)
        self.setFixedHeight(5)
        self.set_video(video)
        self.sliderMoved.connect(self.onSliderMoved)
        self.set_video(video)

    def set_video(self, video: VideoModel|None):
        self._video = video
        if self._video is not None:
            self._video.ready_changed.connect(self.onVideoReadyChanged)
            self._video.frame_id_changed.connect(self.setValue)
            self.onVideoReadyChanged(self._video.ready)
        else:
            self.setRange(0, 100)
            self.setValue(100)
            self.setEnabled(False)

    def onSliderMoved(self):
        if self._video is not None:
            self._video.gotoFrameId(self.value())

    def onVideoReadyChanged(self, ready: bool):
        self.setEnabled(self._video.valid)
        if self._video.valid:
            self.setMaximum(self._video.n_frames - 1)
            self.setValue(self._video.frame_id)

    def mousePressEvent(self, event):
        QSlider.mousePressEvent(self, event)
        if event.button() == Qt.MouseButton.LeftButton:
            frame_id = self.pixelPosToRangeValue(event.pos())
            self._video.gotoFrameId(frame_id)
        
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
