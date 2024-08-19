import argparse as ap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget
# ##############################################################
from src.models.video_file import VideoFile
from src.models.timeline_list import TimelineListModel
from src.models.time_window import TimeWindowModel
from src.views.player import Player
from src.views.timeline_list import TimelineListView
from src.icons import Icons
# ##############################################################

parser = ap.ArgumentParser()
parser.add_argument('video_path')
args = parser.parse_args()

app         = QApplication([])

# models
video_file      = VideoFile(args.video_path)
assert video_file.error == "", video_file.error
timeline_list   = TimelineListModel(video_file.n_frames)
time_window     = TimeWindowModel.from_video_file(video_file)

# views
player_view         = Player(video_file)
timeline_list_view  = TimelineListView(timeline_list, time_window)

# compose main window
window      = QMainWindow()
window.setWindowTitle("YAVAT - Yet Another Video Annotation Tool")
window.setWindowIcon(Icons.Yavat.icon())
window.setCentralWidget(player_view)
dock        = QDockWidget("Timelines")
dock.setWidget(timeline_list_view)
dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock) #, Qt.Orientation.Vertical)

window.show()
app.exec()

