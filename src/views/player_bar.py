from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QToolBar
from PyQt6.QtGui import QAction, QKeySequence
from src.icons import Icons
from src.models.video import VideoModel
from src.widgets.spacer import Spacer
from src.views.position_editor import PositionEditor
from src.views.frame_id_editor import FrameIdEditor

class PlayerBarView(QToolBar):
    def __init__(self, video: VideoModel|None=None, parent: QWidget|None = None):
        QToolBar.__init__(self, parent)
        self._video: VideoModel|None = None
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
        self._backward_step_act.setToolTip("Move Backward 1 frame (Ctrl + LeftArrow)")
        self._backward_step_act.triggered.connect(self.onBackwardStep)
        self._backward_step_act.setIcon(Icons.BackwardStep.icon())
        self._backward_step_act.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Left))
        self.addAction(self._backward_step_act)

        self._frame_id_editor = FrameIdEditor()
        self.addWidget(self._frame_id_editor)
        self._position_editor = PositionEditor()
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
        self._sound_act.setShortcut(Qt.Key.Key_M)
        self.addAction(self._sound_act)
                
        self.set_video(video)

    def set_video(self, video: VideoModel|None):
        self._frame_id_editor.set_video(video)
        self._position_editor.set_video(video)
        if self._video is not None:
            self._video.ready_changed.disconnect(self.onVideoReadyChanged)
            self._video.player.playingChanged.disconnect(self.onVideoPlayingChanged)
        self._video = video
        if self._video is not None:
            self._video.ready_changed.connect(self.onVideoReadyChanged)
            self._video.player.playingChanged.connect(self.onVideoPlayingChanged)
            self.onVideoReadyChanged(self._video.ready)
        else:
            self.setEnabled(False)

    def onVideoReadyChanged(self, ready: bool):
        self.setEnabled(self._video.valid)
        if self._video.valid:
            self.onVideoPlayingChanged(self._video.playing)
            if self._video.player.hasAudio():
                self._video._audio_output.mutedChanged.connect(self.onVideoMutedChanged)
                self.onVideoMutedChanged(self._video._audio_output.isMuted())
            else:
                self._sound_act.setEnabled(False)
                self._sound_act.setIcon(Icons.Mute.icon())
                self._sound_act.setToolTip("No Audio Stream")

    def onVideoPlayingChanged(self, playing: bool):
        self._play_act.setIcon(Icons.Pause.icon() if playing else Icons.Play.icon())
        self._play_act.setToolTip("Pause (Space)" if playing else "Play (Space)")

    def onVideoMutedChanged(self, muted: bool):
        self._sound_act.setIcon(Icons.Mute.icon() if muted else Icons.Sound.icon())
        self._sound_act.setToolTip("Un-Mute (M)" if muted else "Mute (M)")

    def onActPlay(self):
        if self._video.player.isPlaying():
            self._video.pause()
        else:
            self._video.play()
        
    def onActSound(self):
        self._video._audio_output.setMuted(not self._video._audio_output.isMuted())
        
    def onBackward(self): 
        self._move(-round(self._video.fps))
    
    def onForward(self): 
        self._move(round(self._video.fps))

    def onBackwardStep(self, n_frames: int=1):
        self._move(-1)
    
    def onForwardStep(self, n_frames: int=1): 
        self._move(1)

    def _move(self, n_frames: int):
        frame_id        = self._video.frame_id
        new_frame_id    = (frame_id + n_frames) % self._video.n_frames
        self._video.gotoFrameId(new_frame_id)

