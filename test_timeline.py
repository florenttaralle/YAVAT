from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from typing import List
# #######################################################################
from src.models.timeline import TimeLineModel
from src.views.timeline import TimeLineView
# #######################################################################

X_MAX = 30

app = QApplication([])

timeline = TimeLineModel(30, "Name")
timeline.add_range(1, 4, "RE-0")
timeline.add_range(6, 12, "RE-1")
timeline.add_ponctual(14, "PE-2")
timeline.add_ponctual(16, "PE-3")
timeline.add_range(20, 24, "RE-4")

view = TimeLineView(timeline)
view.setFixedHeight(150)

window = QMainWindow()
window.setCentralWidget(view)
window.show()

app.exec()
