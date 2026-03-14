import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDockWidget

from src.models.application_state import ApplicationStateModel, AppConfig, YavatModel
from src.views.player import PlayerView
from src.views.annotations import AnnotationTreeView
from src.views.dialogs.annotation_color import exec_annotation_color_dialog
from src.icons import Icons

class YavatView(QMainWindow):
    VIDEO_EXT       = ["*.avi", "*.mp4"]
    YAVAT_EXT       = ["*.yavat", "*.yvt"]
    
    def __init__(self, app_config: AppConfig, path: str|None=None):
        QMainWindow.__init__(self)
        self.state = ApplicationStateModel(app_config)
        # build the gui
        self._player_view       = PlayerView()
        self._annotations_view  = AnnotationTreeView(self.state)
        self._player_view.muted_changed.connect(self._on_player_mute_changed)
        self._annotations_view.color_icon_clicked.connect(self._on_annotation_color_icon_clicked)

        # set global font size from config
        self._set_app_font_from_config()
        # set player mute from persisted config
        self._player_view.set_muted(self.state.config.mute)
        
        # build the GUI
        self.setWindowTitle("YAVAT - Yet Another Video Annotation Tool")
        self.setWindowIcon(Icons.Yavat.icon())
        self.setCentralWidget(self._player_view)

        # build a dockable window for the annotaion tree
        annotations_dock = QDockWidget("Annotations", self)
        annotations_dock.setWidget(self._annotations_view)
        annotations_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, annotations_dock, Qt.Orientation.Horizontal)

        # add menu for save/load annotations
        file_menu = self.menuBar().addMenu("&File")
        act_load = file_menu.addAction(Icons.Load.icon(), "Load")
        act_load.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_O))
        act_load.triggered.connect(self._on_act_load)
        # add menu to quit application
        file_menu.addSeparator()
        act_quit = file_menu.addAction(Icons.Quit.icon(), "Quit")
        act_quit.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Q))
        act_quit.triggered.connect(self.close)

        # set global shortcuts        
        QShortcut(QKeySequence("Ctrl+Shift+="), self, activated=lambda: self._change_app_font(+1))
        QShortcut(QKeySequence("Ctrl+Shift+-"), self, activated=lambda: self._change_app_font(-1))
        
        # connect signals & slots
        self.state.watched_active_annotation.changed.connect(self._on_active_annotation_changed)
        self.state.watched_yavat.changed.connect(self._on_yavat_changed)

        # init main yavat object
        self.state.set_yavat(None) # ensure proper initialization
        # try to load if any path provided
        if path is not None:
            self._load(path)


    def _set_app_font_from_config(self):
        app = QApplication.instance()
        font = app.font()        
        font.setPointSize(self.state.config.font_size)
        app.setFont(font)

    def _change_app_font(self, delta: int):
        self.state.config.font_size = max(self.state.config.MIN_FONT_SIZE, min(self.state.config.MAX_FONT_SIZE, self.state.config.font_size + delta))
        self.state.config.save()
        self._set_app_font_from_config()
        
    def _on_active_annotation_changed(self, active_annotation):
        if active_annotation is not None:
            print(f"Item Selected: {active_annotation}")
        else:
            print("No More Item Selected")

    def _on_player_mute_changed(self, muted: bool):
        muted = bool(muted)
        if muted != self.state.config.mute:
            self.state.config.mute = muted
            self.state.config.save()

    def _on_annotation_color_icon_clicked(self, annotation):
        video = self.state.yavat.video if self.state.yavat is not None else None
        was_playing = bool(video is not None and video.valid and video.playing)
        if was_playing:
            video.pause()
        try:
            exec_annotation_color_dialog(
                annotation,
                self,
                preferred_color=self.state.config.default_color,
            )
        finally:
            if was_playing:
                video.play()

    def _on_yavat_changed(self, yavat: YavatModel|None):
        # disconnect previous yavat
        if self.state.yavat is not None:
            self._player_view.set_video(None)
            self.state.set_active_annotation(None)
            self._annotations_view.set_annotations(None)
            self.state.set_time_window(None)

        if yavat is not None:
            yavat.video.ready_changed.connect(self._on_video_ready_changed)
            self._annotations_view.set_annotations(yavat.annotations)

    def _on_video_ready_changed(self, ready: bool):
        self._player_view.set_video(self.state.yavat.video)
        self.state.set_time_window(self.state.yavat.time_window)
        if self.state.yavat.video.valid and self.state.config.auto_play:
            self.state.yavat.video.play()

    def _on_act_close_file(self):
        self.state.set_yavat(None)

    def _on_act_load(self):
        # look for file in current yavat folder if one available
        if self.state.yavat and self.state.yavat.yavat_path:
            # look for the yavat file first
            folder = os.path.dirname(self.state.yavat.yavat_path)
        elif self.state.yavat:
            # look for the video file second
            folder = os.path.dirname(self.state.yavat.video.path)
        else:
            folder = None
        
        filename,  _ = QFileDialog.getOpenFileName(None, "Load YAVAT annotations", 
                                            folder,
                                            ";;".join([
                                                "Video or YAVAT ({ext})".format(ext=" ".join(self.VIDEO_EXT + self.YAVAT_EXT)),
                                                "Video ({ext})".format(ext=" ".join(self.VIDEO_EXT)),
                                                "YAVAT Annotations ({ext})".format(ext=" ".join(self.YAVAT_EXT)),
                                                "All (*)",
                                            ]))
        if filename == '': return
        self._load(filename)
    
    def _load(self, path: str):
        try:
            yavat = YavatModel.load(path, self.state.config.default_color)
        except Exception as what:
            QMessageBox.warning(self, "Error Loading", str(what), QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            return
        # update views with it
        self.state.set_yavat(yavat)
