import argparse as ap
from PyQt6.QtWidgets import QApplication, QMainWindow
from src.models.video_file import VideoFile
from src.views.player import Player
from src.icons import Icons

parser = ap.ArgumentParser()
parser.add_argument('video_path')
args = parser.parse_args()

app         = QApplication([])

video_file  = VideoFile(args.video_path)
player      = Player(video_file)

window      = QMainWindow()
window.setWindowTitle("YAVAT - Yet Another Video Annotation Tool")
window.setWindowIcon(Icons.Yavat.icon())
window.setCentralWidget(player)
window.show()
app.exec()

