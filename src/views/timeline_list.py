from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QAbstractItemView, QSizePolicy
from typing import Mapping
from src.models.time_window import TimeWindowModel
from src.models.timeline_list import TimeLineListModel, TimeLineModel
from src.views.timeline import TimeLineView


class TimeLineListView(QListWidget):
    def __init__(self, timeline_list: TimeLineListModel, time_window: TimeWindowModel, event_h: float=0.8, parent: QWidget|None = None):
        QListWidget.__init__(self, parent)
        self._timeline_list     = timeline_list
        self._time_window       = time_window
        self._widget_items:     Mapping[TimeLineView, QListWidgetItem] = {}
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        timeline_list.timeline_added.connect(self.onTimeLineListItemAdded)
        timeline_list.timeline_removed.connect(self.onTimeLineListItemRemoved)
        for timeline in timeline_list:
            self.onTimeLineListItemAdded(timeline)

    def onTimeLineListItemAdded(self, timeline: TimeLineModel):
        view                        = TimeLineView(timeline, self._time_window)
        widget                      = QListWidgetItem()
        widget.setSizeHint(view.minimumSizeHint())
        self._widget_items[view]    = widget
        self.addItem(widget)
        self.setItemWidget(widget, view)
        widget.setSelected(True)
    
    def _timeline_view(self, timeline: TimeLineModel) -> TimeLineView:
        for view in self._widget_items.keys():
            if view.timeline is timeline:
                return view
        raise ValueError("Not Found")

    def _timeline_row(self, timeline: TimeLineModel) -> int:
        view    = self._timeline_view(timeline)
        widget  = self._widget_items[view]
        for row in range(self.count()):
            if self.item(row) is widget:
                return row
        raise ValueError("Not Found")

    def selected_timeline(self) -> TimeLineModel|None:
        widgets = self.selectedItems()
        if len(widgets) == 0: return None
        widget = widgets[0]
        for view, widget_ in self._widget_items.items():
            if widget_ is widget:
                return view.timeline
        return None

    def onTimeLineListItemRemoved(self, timeline: TimeLineModel):
        row = self._timeline_row(timeline)
        self.takeItem(row)
