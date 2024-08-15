from PyQt6.QtWidgets import QApplication, QMainWindow
from src.models.video_file import VideoFile
from src.views.player_bar import PlayerBar


PATH = "/media/florent/secondary_dd/datasets/youtube_shorts/high/ZmXMLh006yU_1080p/video.mp4"

app = QApplication([])

video_file = VideoFile(PATH)
player_bar = PlayerBar(video_file)

window = QMainWindow()
window.setCentralWidget(player_bar)
window.show()

app.exec()
