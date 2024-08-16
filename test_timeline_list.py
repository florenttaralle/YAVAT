from PyQt6.QtWidgets import QApplication, QMainWindow
# #######################################################################
from src.models.timeline_list import TimeLineListModel
from src.models.time_window import TimeWindowModel
from src.views.timeline_list import TimeLineListView
from src.icons import Icons
# #######################################################################

X_MAX = 100

app = QApplication([])

timeline_list   = TimeLineListModel(X_MAX)
time_window     = TimeWindowModel(X_MAX)
view            = TimeLineListView(timeline_list, time_window)

window = QMainWindow()
menu = window.menuBar().addMenu("&Timelines")
add_action = menu.addAction(Icons.Timeline.icon(), "Add")
add_action.triggered.connect(lambda _: timeline_list.add())
rem_action = menu.addAction(Icons.Delete.icon(), "Remove")
rem_action.setEnabled(False)

def itemSelectionChanged():
    rem_action.setEnabled(view.selected_timeline() is not None)
view.itemSelectionChanged.connect(itemSelectionChanged)

def delete_item(*_):
    timeline = view.selected_timeline()
    timeline_list.rem(timeline)
rem_action.triggered.connect(delete_item) 

window.setCentralWidget(view)
window.show()

app.exec()
