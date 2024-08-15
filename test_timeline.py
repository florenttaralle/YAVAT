from PyQt6.QtWidgets import QApplication, QMainWindow
# #######################################################################
from src.models.timeline import TimeLineModel
from src.models.time_window import TimeWindowModel
from src.views.timeline import TimeLineView
# #######################################################################

X_MAX = 100

app = QApplication([])

timeline    = TimeLineModel(X_MAX, "Name")
time_window = TimeWindowModel(timeline.duration)

view = TimeLineView(timeline, time_window)
view.setFixedHeight(100)

window = QMainWindow()
window.setCentralWidget(view)
window.show()

app.exec()
