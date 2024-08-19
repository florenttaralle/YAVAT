from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QAbstractItemView
from typing import Mapping
from src.models.time_window import TimeWindowModel
from src.models.timeline_list import TimelineListModel, TimelineModel
from src.models.timeline_list_state import TimelineListState
from src.views.timeline import TimelineView


class TimelineListListView(QListWidget):
    edit_timeline_name = pyqtSignal(TimelineModel)
    "SIGNAL: edit_timeline_name(timeline: TimelineModel)"
    
    def __init__(self, timeline_list: TimelineListModel, state: TimelineListState,
                 time_window: TimeWindowModel, parent: QWidget|None = None):
        QListWidget.__init__(self, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self._timeline_list     = timeline_list
        self._state             = state
        self._time_window       = time_window
        self._widgets:          Mapping[TimelineView, QListWidgetItem] = {}
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # events from the view
        self.itemSelectionChanged.connect(self.onSelectionChanged)
        # events from the model
        state.timeline_added.connect(self.onTimelineListItemAdded)
        state.timeline_removed.connect(self.onTimelineListItemRemoved)
        # populate with existing items
        for timeline in timeline_list:
            self.onTimelineListItemAdded(timeline)

    def onSelectionChanged(self):
        widgets = self.selectedItems()
        if len(widgets):
            selected_timeline = self._widget_to_timeline(widgets[0])
        else:
            selected_timeline = None
        self._state.set_selection(selected_timeline)

    def onTimelineListItemAdded(self, timeline: TimelineModel):
        view                        = TimelineView(timeline, self._time_window)
        widget                      = QListWidgetItem()
        self._widgets[view]         = widget
        self.addItem(widget)
        self.setItemWidget(widget, view)
        widget.setSizeHint(view.minimumSizeHint())
        widget.setSelected(True)
        self._state[timeline].visible_changed.connect(
            lambda _, visible: widget.setHidden(not visible))
        view.edit_timeline_name.connect(self.edit_timeline_name)
    
    def onTimelineListItemRemoved(self, timeline: TimelineModel):
        row = self._timeline_row(timeline)
        self.takeItem(row)

    def _widget_to_timeline(self, widget: QListWidgetItem) -> TimelineModel:
        for view, widget_ in self._widgets.items():
            if widget is widget_:
                return view.timeline
        raise ValueError("Widget not Found")

    def _timeline_view(self, timeline: TimelineModel) -> TimelineView:
        for view in self._widgets.keys():
            if view.timeline is timeline:
                return view
        raise ValueError("Not Found")

    def _timeline_row(self, timeline: TimelineModel) -> int:
        view    = self._timeline_view(timeline)
        widget  = self._widgets[view]
        for row in range(self.count()):
            if self.item(row) is widget:
                return row
        raise ValueError("Not Found")
