import os, argparse as ap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget
from PyQt6.QtGui import QKeySequence
# ##############################################################
from src.models.video_file import VideoFile
from src.models.time_window import TimeWindowModel
from src.views.player import Player
from src.views.timeline_list import TimelineListView, TimelineListModel
from src.views.timeseries_list import TimeseriesListView, TimeseriesListModel
from src.icons import Icons
from src.save_n_load import SaveAndLoad
# ##############################################################

parser = ap.ArgumentParser()
parser.add_argument('video_path')
parser.add_argument('-l', '--labels_path', default=None)
parser.add_argument('-t', '--timeline', action='append', default=[])
args = parser.parse_args()

app             = QApplication([])

# models
video_file      = VideoFile(args.video_path)
assert video_file.error == "", video_file.error
timeline_list   = TimelineListModel(video_file.n_frames)
timeseries_list = TimeseriesListModel(video_file.n_frames)
time_window     = TimeWindowModel.from_video_file(video_file)
save_n_load     = SaveAndLoad(video_file, timeline_list, timeseries_list)
# create provided timeline names if any provided
for timeline_name in args.timeline:
    timeline_list.add(timeline_name)
# open label file if any provided
if args.labels_path is not None:
    save_n_load.load_file(args.labels_path)
else:
    # try to auto-find .yavat with same name
    labels_path = os.path.splitext(args.video_path)[0] + ".yavat"
    if os.path.exists(labels_path):
        save_n_load.load_file(labels_path)

# views
player_view         = Player(video_file)
timeline_list_view  = TimelineListView(timeline_list, time_window)
timeseries_view     = TimeseriesListView(timeseries_list, time_window)

# compose main window
window      = QMainWindow()
window.setWindowTitle("YAVAT - Yet Another Video Annotation Tool")
window.setWindowIcon(Icons.Yavat.icon())
window.setCentralWidget(player_view)

timelines_dock        = QDockWidget("Timelines")
timelines_dock.setWidget(timeline_list_view)
timelines_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, timelines_dock, Qt.Orientation.Vertical)

timeseries_dock        = QDockWidget("Timeseries")
timeseries_dock.setWidget(timeseries_view)
timeseries_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, timeseries_dock, Qt.Orientation.Vertical)
timeseries_dock.setVisible(len(timeseries_list) > 0)

# add menu for save/load annotations (here is dirty)
file_menu = window.menuBar().addMenu("&File")
act_load = file_menu.addAction(Icons.Load.icon(), "&Load Annotations")
act_load.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_O))
act_load.triggered.connect(save_n_load.pick_and_load)
act_save = file_menu.addAction(Icons.Save.icon(), "&Save Annotations")
act_save.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S))
act_save.triggered.connect(save_n_load.pick_and_save)
file_menu.addSeparator()
act_quit = file_menu.addAction(Icons.Quit.icon(), "&Quit")
act_quit.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Q))
act_quit.triggered.connect(app.quit)

# add menu for views
view_menu = window.menuBar().addMenu("&View")
view_menu.addAction(timelines_dock.toggleViewAction())
view_menu.addAction(timeseries_dock.toggleViewAction())

window.show()
app.exec()

