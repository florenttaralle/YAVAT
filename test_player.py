import argparse as ap
from PyQt6.QtWidgets import QApplication, QMainWindow
from src.models.video_file import VideoFile
from src.views.player import Player

parser = ap.ArgumentParser()
parser.add_argument('video_path')
args = parser.parse_args()

app         = QApplication([])
video_file  = VideoFile(args.video_path)
window      = QMainWindow()
player      = Player(video_file)
window.setCentralWidget(player)
window.show()
app.exec()

