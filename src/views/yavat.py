import os

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QCloseEvent, QFont, QFontMetrics, QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDockWidget, QToolBar, QProxyStyle, QStyle, QColorDialog, QInputDialog

from src.models.application_state import ApplicationStateModel, AppConfig, YavatModel
from src.views.player import PlayerView
from src.views.annotations import AnnotationTreeView
from src.views.dialogs.annotation_color import exec_annotation_color_dialog
from src.icons import Icons
from . import menus

class _IconSizeProxyStyle(QProxyStyle):
    def __init__(self, base_style):
        QProxyStyle.__init__(self, base_style)
        self._icon_side = 16

    def set_icon_side(self, side: int):
        self._icon_side = max(8, int(side))

    def pixelMetric(self, metric, option=None, widget=None):
        if metric in (
            QStyle.PixelMetric.PM_SmallIconSize,
            QStyle.PixelMetric.PM_ToolBarIconSize,
            QStyle.PixelMetric.PM_ButtonIconSize,
        ):
            return self._icon_side
        return QProxyStyle.pixelMetric(self, metric, option, widget)


class YavatView(QMainWindow):
    VIDEO_EXT       = ["*.avi", "*.mp4"]
    YAVAT_EXT       = ["*.yavat", "*.yvt"]
    
    def __init__(self, app_config: AppConfig, path: str|None=None):
        QMainWindow.__init__(self)
        self.state = ApplicationStateModel(app_config)
        self._icon_style = None
        # build the gui
        self._player_view       = PlayerView()
        self._annotations_view  = AnnotationTreeView(self.state)
        self._player_view.muted_changed.connect(self._on_player_mute_changed)
        self._annotations_view.color_icon_clicked.connect(self._on_annotation_color_icon_clicked)

        # set player mute from persisted config
        self._player_view.set_muted(self.state.config.mute)

        # add a callback to update IHM with yavat status
        self.state.watched_yavat.changed.connect(self._on_yavat_changed)
        
        # build the GUI
        self.setWindowTitle("YAVAT - Yet Another Video Annotation Tool")
        self.setWindowIcon(Icons.Yavat.icon())
        self.setCentralWidget(self._player_view)

        # build a dockable window for the annotaion tree
        annotations_dock = QDockWidget("Annotations", self)
        annotations_dock.setWidget(self._annotations_view)
        annotations_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, annotations_dock, Qt.Orientation.Horizontal)

        # add file menu
        self._file_menu = menus.FileMenu()
        self._file_menu.on_load.connect(self._on_act_load)
        self._file_menu.on_save.connect(self._save)
        self._file_menu.on_quit.connect(self.close) # self.close will call the onCloseEvent
        self.menuBar().addMenu(self._file_menu)
        # add config menu
        self._config_menu = menus.ConfigMenu()
        self._config_menu.set_auto_play(self.state.config.auto_play)
        self._config_menu.set_default_color(self.state.config.default_color)
        self._config_menu.on_text_bigger.connect(lambda: self._change_app_font(+1))
        self._config_menu.on_text_smaller.connect(lambda: self._change_app_font(-1))
        self._config_menu.on_graph_height.connect(self._on_graph_height)
        self._config_menu.on_auto_play.connect(self._on_auto_play_changed)
        self._config_menu.on_default_color.connect(self._on_default_color_changed)
        self.menuBar().addMenu(self._config_menu)
        
        # apply globaly icon size and font size
        self._set_app_font_from_config()
        QTimer.singleShot(0, self._set_app_font_from_config)

        # connect signals & slots
        self.state.watched_active_annotation.changed.connect(self._on_active_annotation_changed)
        self.state.watched_yavat.changed.connect(self._on_yavat_changed)

        # init main yavat object
        self.state.set_yavat(None) # ensure proper initialization
        # try to load if any path provided
        if path is not None:
            self._load(path)

    def _on_yavat_changed(self, yavat: YavatModel|None):
        self._file_menu.set_can_save(yavat is not None)

    def _set_app_font_from_config(self):
        app = QApplication.instance()
        font = QFont(app.font())
        font.setPointSize(self.state.config.font_size)
        # Apply style-driven icon metrics first; style changes can repolish fonts.
        self._set_app_icon_size_from_font(font)
        app.setFont(font)
        self.setFont(font)
        self.menuBar().setFont(font)
        self._player_view.setFont(font)
        self._annotations_view.setFont(font)

    def _set_app_icon_size_from_font(self, font=None):
        if font is None:
            font = QApplication.instance().font()
        side = max(8, QFontMetrics(font).height() - 2)
        icon_size = QSize(side, side)
        app = QApplication.instance()
        if self._icon_style is None:
            self._icon_style = _IconSizeProxyStyle(app.style())
        self._icon_style.set_icon_side(side)
        app.setStyle(self._icon_style)
        self.setIconSize(icon_size)
        for toolbar in self.findChildren(QToolBar):
            toolbar.setIconSize(icon_size)
        self._annotations_view.setIconSize(icon_size)
        self._config_menu.set_default_color(self.state.config.default_color)

    def _change_app_font(self, delta: int):
        self.state.config.font_size = max(self.state.config.MIN_FONT_SIZE, min(self.state.config.MAX_FONT_SIZE, self.state.config.font_size + delta))
        self.state.config.save()
        self._set_app_font_from_config()
        
    def _on_active_annotation_changed(self, active_annotation):
        if active_annotation is not None:
            print(f"Item Selected: {active_annotation}")
        else:
            print("No More Item Selected")

    def _on_graph_height(self):
        value, ok = QInputDialog.getInt(
            self,
            "Graphs min height",
            "Minimum graph height:",
            self.state.config.annotation_graph_height,
            0,
            500,
            1,
        )
        if not ok:
            return
        if value == self.state.config.annotation_graph_height:
            return
        self.state.config.annotation_graph_height = value
        self.state.config.save()
        self._annotations_view.onTimeWindowChanged(self.state.time_window)

    def _on_player_mute_changed(self, muted: bool):
        muted = bool(muted)
        if muted != self.state.config.mute:
            self.state.config.mute = muted
            self.state.config.save()

    def _on_auto_play_changed(self, auto_play: bool):
        auto_play = bool(auto_play)
        if auto_play != self.state.config.auto_play:
            self.state.config.auto_play = auto_play
            self.state.config.save()

    def _on_default_color_changed(self):
        color = QColorDialog.getColor(self.state.config.default_color, self, "Default annotation color")
        if not color.isValid():
            return
        if color == self.state.config.default_color:
            return
        self.state.config.default_color = color
        self.state.config.save()
        self._config_menu.set_default_color(color)

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
        self.state.yavat_hash = None

    def _yavat_not_saved(self) -> bool:
        if self.state.yavat is None:
            return False
        _, json_hash = self.state.yavat.serialize()
        return self.state.yavat_hash != json_hash        

    def _on_act_quit(self):
        if self._yavat_not_saved():
            if self._hask_and_save() == QMessageBox.StandardButton.Cancel:
                return
        self.close()

    def closeEvent(self, event: QCloseEvent):
        if self._yavat_not_saved():
            if self._hask_and_save() == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        QMainWindow.closeEvent(self, event)

    def _on_act_load(self):
        if self._yavat_not_saved():
            if self._hask_and_save() == QMessageBox.StandardButton.Cancel:
                return # user canceled
            if not self._save():
                return # user canceled (did not choose a file to save)
        
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
            yavat, json_hash = YavatModel.load(path, self.state.config.default_color)
        except Exception as what:
            QMessageBox.warning(self, "Error Loading", str(what), QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            return
        self.state.set_yavat(yavat)
        self.state.yavat_hash = json_hash

    def _hask_and_save(self) -> QMessageBox.StandardButton:
        result = QMessageBox.question(
            self,
            "Unsaved changes",
            "Some current work has not been saved.\nDo you want to save before continuing?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes,
        )        
        if result == QMessageBox.StandardButton.Yes:
            saved = self._save()   
            result = QMessageBox.StandardButton.Yes if saved else QMessageBox.StandardButton.Cancel
        return result

    def _save(self) -> bool:
        if self.state.yavat is None:
            return False

        if self.state.yavat.yavat_path is None:
            default_path = YavatModel.default_path(self.state.yavat.video.path)
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save YAVAT annotations",
                default_path,
                "YAVAT Annotations ({ext})".format(ext=" ".join(self.YAVAT_EXT)),
            )
            if filename == "":
                return False
        else:
            filename = None

        try:
            json_hash = self.state.yavat.save(filename)
        except Exception as what:
            QMessageBox.warning(
                self,
                "Error Saving",
                str(what),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
            return False

        self.state.yavat_hash = json_hash
        return True
    
