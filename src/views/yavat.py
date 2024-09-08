from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import os
from src.models.yavat import YavatModel
from src.views.player import PlayerView
from src.views.annotation_list import AnnotationListView
from src.views.dialogs.data_import import DataImportDialog
from src.models.profile import ProfileModel
from src.views.values_grid import ValuesGridView
from src.icons import Icons

class YavatView(QMainWindow):
    def __init__(self, path: str|None=None, profile_path: str|None=None):
        QMainWindow.__init__(self)
        self._yavat:            YavatModel|None = None
        self._player_view       = PlayerView()
        self._annotations_view  = AnnotationListView()
        self._values_grid_view  = ValuesGridView()
        self._profile           = ProfileModel()

        self.setWindowTitle("YAVAT - Yet Another Video Annotation Tool")
        self.setWindowIcon(Icons.Yavat.icon())
        self.setCentralWidget(self._player_view)

        values_grid_dock = QDockWidget("Current Values", self)
        values_grid_dock.setWidget(self._values_grid_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, values_grid_dock, Qt.Orientation.Vertical)

        annotations_dock = QDockWidget("Annotations", self)
        annotations_dock.setWidget(self._annotations_view)
        annotations_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, annotations_dock, Qt.Orientation.Vertical)

        # add menu for save/load annotations
        file_menu = self.menuBar().addMenu("&File")
        act_load = file_menu.addAction(Icons.Load.icon(), "Load")
        act_load.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_O))
        act_load.triggered.connect(self.onActLoad)
        self._act_save = file_menu.addAction(Icons.Save.icon(), "Save Annotations")
        self._act_save.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S))
        self._act_save.triggered.connect(self.onActSave)
        self._act_save_as = file_menu.addAction(Icons.Save.icon(), "Save Annotations As")
        self._act_save_as.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_S))
        self._act_save_as.triggered.connect(self.onActSaveAs)
        self._act_import_ts = file_menu.addAction(Icons.Import.icon(), "Import Annotations")
        self._act_import_ts.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_I))
        self._act_import_ts.triggered.connect(self.onActImportData)
        self._act_close = file_menu.addAction(Icons.Close.icon(), "Close")
        self._act_close.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_W))
        self._act_close.triggered.connect(self.onActCloseFile)

        file_menu.addSeparator()
        self.act_load_profile = file_menu.addAction(Icons.Load.icon(), "Load Profile")
        self.act_load_profile.triggered.connect(self.onActLoadProfile)
        self.act_use_as_profile = file_menu.addAction(Icons.Save.icon(), "Use as Profile")
        self.act_use_as_profile.triggered.connect(self.onActUseAsProfile)
        self.act_use_as_profile.setEnabled(False)
        self.act_save_profile = file_menu.addAction(Icons.Save.icon(), "Save Profile")
        self.act_save_profile.triggered.connect(self.onActSaveProfile)
        
        file_menu.addSeparator()
        act_quit = file_menu.addAction(Icons.Quit.icon(), "Quit")
        act_quit.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Q))
        act_quit.triggered.connect(self.close)

        # add menu for views
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(annotations_dock.toggleViewAction())
        view_menu.addAction(values_grid_dock.toggleViewAction())

        self.set_yavat(None)
        if path is not None:
            self._load(path)
            
        if profile_path is not None:
            self._load_profile(profile_path)

    def set_yavat(self, yavat: YavatModel|None):
        if self._yavat is not None:
            self._yavat.video.ready_changed.disconnect(self.onVideoReadyChanged)
        self._yavat = yavat
        if self._yavat is not None:
            self._yavat.video.ready_changed.connect(self.onVideoReadyChanged)            
        else:
            self._player_view.set_video(None)
            self._annotations_view.set_context(None, None)
            self._values_grid_view.set_context(None, None)
            
        self._act_save.setEnabled(self._yavat is not None)
        self._act_save_as.setEnabled(self._yavat is not None)
        self._act_import_ts.setEnabled(self._yavat is not None)
        self._act_close.setEnabled(self._yavat is not None)

    def onVideoReadyChanged(self, ready: bool):
        self._player_view.set_video(self._yavat.video)
        self._annotations_view.set_context(self._yavat.time_window, self._yavat.annotations)
        self._values_grid_view.set_context(self._yavat.time_window, self._yavat.annotations)

    def onActCloseFile(self):
        self.set_yavat(None)
        self.act_use_as_profile.setEnabled(False)

    def onActLoad(self):
        if self._yavat and self._yavat.yavat_path:
            folder = os.path.dirname(self._yavat.yavat_path)
        elif self._yavat:
            folder = os.path.dirname(self._yavat.video.path)
        else:
            folder = None
        
        VIDEO_EXT = ["*.avi", "*.mp4"]
        YAVAT_EXT = ["*.yavat", "*.yvt"]
        filename,  _ = QFileDialog.getOpenFileName(None, "Load YAVAT annotations", 
                                            folder,
                                            ";;".join([
                                                "Video or YAVAT ({ext})".format(ext=" ".join(VIDEO_EXT + YAVAT_EXT)),
                                                "Video ({ext})".format(ext=" ".join(VIDEO_EXT)),
                                                "YAVAT Annotations ({ext})".format(ext=" ".join(YAVAT_EXT)),
                                                "All (*)",
                                            ]))
        if filename == '': return
        self._load(filename)
    
    def onActSave(self):
        if self._yavat.yavat_path:
            self._save()
        else:
            self.onActSaveAs()
        
    def onActSaveAs(self):
        default_path = self._yavat.yavat_path or \
            self._yavat.default_path(self._yavat.video.path)
        filename, _ = QFileDialog.getSaveFileName(None, 
                                                  "Save YAVAT annotations",
                                                  default_path,
                                                  "YAVAT Annotations (*.json, *.yavat, *.yvt)")
        if filename == '': return
        self._save(filename)

    def _save(self, path: str|None=None):
        try:
            self._yavat.save(path)
        except Exception as what:
            QMessageBox.warning(self, "Error Saving", str(what), QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        
    def _load(self, path: str):
        try:
            yavat = YavatModel.load(path)
        except Exception as what:
            QMessageBox.warning(self, "Error Loading", str(what), QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        self.act_use_as_profile.setEnabled(True)

        try:
            self._profile.update_annotations(yavat.annotations, True)
        except Exception as what:
            QMessageBox.warning(self, "Error Applying Profile", str(what), QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)

        self.set_yavat(yavat)

    def onActImportData(self):
        DataImportDialog.import_from_file(self._yavat, self._profile, self)
    
    def _load_profile(self, path: str):
        self._profile = ProfileModel.load(path)
        if self._yavat is not None:
            self._profile.update_annotations(self._yavat.annotations, True)

    def onActLoadProfile(self):
        filename, _ = QFileDialog.getOpenFileName(None, 
                                                  "Load YAVAT Profile",
                                                  self._profile.path,
                                                  "YAVAT Profile (*.json, *.yavat_profile, *.yvtp)")
        if filename == '': return
        self._load_profile(filename)
    
    def onActUseAsProfile(self):
        if self._yavat is not None:
            old_path = self._profile.path
            self._profile = ProfileModel.from_annotations(self._yavat.annotations)
            self._profile.path = old_path

    def onActSaveProfile(self):
        filename, _ = QFileDialog.getSaveFileName(None, 
                                                  "Save YAVAT Profile",
                                                  self._profile.path,
                                                  "YAVAT Profile (*.json, *.yavat_profile, *.yvtp)")
        if filename == '': return
        self._profile.save(filename)

    