from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QToolBar
from PyQt6.QtGui import QAction, QKeySequence
from src.icons import Icons
from src.models.video_file import VideoFile
from src.widgets.spacer import Spacer
from src.views.position_editor import PositionEditor
from src.views.frame_id_editor import FrameIdEditor

class PlayerBar(QToolBar):
    def __init__(self, video_file: VideoFile, parent: QWidget|None = None):
        QToolBar.__init__(self, parent)
        self._video_file = video_file
        self.setFixedHeight(36)
        self.setMovable(False)

        self._play_act = QAction()
        self._play_act.triggered.connect(self.onActPlay)
        self._play_act.setShortcut(Qt.Key.Key_Space)
        self.addAction(self._play_act)
                
        self.addWidget(Spacer())

        self._backward_act = QAction()
        self._backward_act.setToolTip("Move Backward 1 sec (LeftArrow)")
        self._backward_act.triggered.connect(self.onBackward)
        self._backward_act.setIcon(Icons.Backward.icon())
        self._backward_act.setShortcut(Qt.Key.Key_Left)
        self.addAction(self._backward_act)

        self._backward_step_act = QAction()
        self._backward_step_act.setToolTip("Move Backward 1 frame (Ctrl+LeftArrow)")
        self._backward_step_act.triggered.connect(self.onBackwardStep)
        self._backward_step_act.setIcon(Icons.BackwardStep.icon())
        self._backward_step_act.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Left))
        self.addAction(self._backward_step_act)

        self._frame_id_editor = FrameIdEditor(video_file)
        self.addWidget(self._frame_id_editor)
        self._position_editor = PositionEditor(video_file)
        self.addWidget(self._position_editor)

        self._forward_step_act = QAction()
        self._forward_step_act.setToolTip("Move Forward 1 frame (Ctrl+RightArrow)")
        self._forward_step_act.triggered.connect(self.onForwardStep)
        self._forward_step_act.setIcon(Icons.ForwardStep.icon())
        self._forward_step_act.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Right))
        self.addAction(self._forward_step_act)

        self._forward_act = QAction()
        self._forward_act.setToolTip("Move Forward 1 sec (RightArrow)")
        self._forward_act.triggered.connect(self.onForward)
        self._forward_act.setIcon(Icons.Forward.icon())
        self._forward_act.setShortcut(Qt.Key.Key_Right)
        self.addAction(self._forward_act)

        self.addWidget(Spacer())

        self._sound_act = QAction()
        self._sound_act.triggered.connect(self.onActSound)
        self.addAction(self._sound_act)
                
        self._video_file.ready_changed.connect(self.onVideoFileReadyChanged)
        self._video_file.player.playingChanged.connect(self.onVideoFilePlayingChanged)

    def onVideoFileReadyChanged(self, ready: bool):
        self.setEnabled(self._video_file.valid)
        if self._video_file.valid:
            self.onVideoFilePlayingChanged(self._video_file.player.isPlaying())
            if self._video_file.player.audioOutput() is not None:
                self._video_file.player.audioOutput().mutedChanged(self.onVideoFileMutedChanged)
                self.onVideoFileMutedChanged(self._video_file.player.audioOutput().isMuted())
            else:
                self._sound_act.setEnabled(False)
                self._sound_act.setIcon(Icons.Mute.icon())
                self._sound_act.setToolTip("No Audio Stream")

    def onVideoFilePlayingChanged(self, playing: bool):
        self._play_act.setIcon(Icons.Pause.icon() if playing else Icons.Play.icon())
        self._play_act.setToolTip("Pause" if playing else "Play")

    def onVideoFileMutedChanged(self, muted: bool):
        self._sound_act.setIcon(Icons.Mute.icon() if muted else Icons.Sound.icon())
        self._sound_act.setToolTip("Un-Mute" if muted else "Mute")

    def onActPlay(self):
        if self._video_file.player.isPlaying():
            self._video_file.pause()
        else:
            self._video_file.play()
        
    def onActSound(self):
        self._video_file.player.audioOutput().setMuted(self._video_file.player.audioOutput().isMuted())
        
    def onBackward(self): 
        self._move(-round(self._video_file.fps))
    
    def onForward(self): 
        self._move(round(self._video_file.fps))

    def onBackwardStep(self, n_frames: int=1):
        self._move(-1)
    
    def onForwardStep(self, n_frames: int=1): 
        self._move(1)

    def _move(self, n_frames: int):
        frame_id        = self._video_file.frame_id
        new_frame_id    = (frame_id +n_frames) % self._video_file.n_frames
        self._video_file.gotoFrameId(new_frame_id)

    def onFrameIdEditingFinished(self):
        print("onFrameIdEditingFinished")
    def onFrameIdInputRejected(self):
        print("onFrameIdInputRejected")
    def onFrameIdReturnPressed(self):
        print("onFrameIdReturnPressed")
    def onFrameIdTextEdited(self, text: str):
        print("onFrameIdTextEdited")

