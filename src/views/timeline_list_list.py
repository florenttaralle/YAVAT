from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QAbstractItemView, QSizePolicy
from typing import Mapping
from src.models.time_window import TimeWindowModel
from src.models.timeline_list import TimeLineListModel, TimeLineModel
from src.views.timeline import TimeLineView


class TimeLineListListView(QListWidget):
    def __init__(self, timeline_list: TimeLineListModel, time_window: TimeWindowModel, fps: float, event_h: float=0.8, parent: QWidget|None = None):
        QListWidget.__init__(self, parent)
        self._timeline_list     = timeline_list
        self._time_window       = time_window
        self._fps               = fps
        self._widget_items:     Mapping[TimeLineView, QListWidgetItem] = {}
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # events from the model
        timeline_list.timeline_added.connect(self.onTimeLineListItemAdded)
        timeline_list.timeline_removed.connect(self.onTimeLineListItemRemoved)
        timeline_list.selected_timeline_changed.connect(self.onTimeLineListSelectedItemChanged)
        # events from the view
        self.itemSelectionChanged.connect(self.onSelectionChanged)
        # populate if required        
        for timeline in timeline_list:
            self.onTimeLineListItemAdded(timeline)

    def onTimeLineListSelectedItemChanged(self, current_timeline: TimeLineModel|None, previous_timeline: TimeLineModel|None):
        if current_timeline is not None:
            view    = self._timeline_view(current_timeline)
            widget  = self._widget_items[view]
            widget.setSelected(True)
        elif previous_timeline is not None:
            view    = self._timeline_view(previous_timeline)
            widget  = self._widget_items[view]
            widget.setSelected(False)

    def onSelectionChanged(self):
        widgets = self.selectedItems()
        if len(widgets):
            selected_timeline = self._widget_to_timeline(widgets[0])
        else:
            selected_timeline = None
        self._timeline_list.selected_timeline = selected_timeline

    def onTimeLineListItemAdded(self, timeline: TimeLineModel):
        view                        = TimeLineView(timeline, self._time_window, self._fps)
        widget                      = QListWidgetItem()
        widget.setSizeHint(view.minimumSizeHint())
        self._widget_items[view]    = widget
        self.addItem(widget)
        self.setItemWidget(widget, view)
    
    def onTimeLineListItemRemoved(self, timeline: TimeLineModel):
        row = self._timeline_row(timeline)
        self.takeItem(row)

    def _widget_to_timeline(self, widget: QListWidgetItem) -> TimeLineModel:
        for view, widget_ in self._widget_items.items():
            if widget is widget_:
                return view.timeline
        raise ValueError("Widget not Found")

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
