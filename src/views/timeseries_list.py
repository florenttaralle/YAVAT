from typing import Mapping
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QAbstractItemView
from src.models.timeseries_list import TimeseriesListModel, TimeseriesModel
from src.models.time_window import TimeWindowModel
from src.views.timeseries import TimeseriesView

class TimeseriesListView(QListWidget):
    def __init__(self, timeseries_list: TimeseriesListModel, time_window: TimeWindowModel, parent: QWidget|None = None):
        QListWidget.__init__(self, parent)
        self._timeseries_list   = timeseries_list
        self._time_window       = time_window
        self._widgets:          Mapping[TimeseriesView, QListWidgetItem] = {}

        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("border: 0px")

        # events from the model
        timeseries_list.timeseries_added.connect(self.onTimeseriesListItemAdded)
        timeseries_list.timeseries_removed.connect(self.onTimeseriesListItemRemoved)
        # populate with existing items
        for timeseries in timeseries_list:
            self.onTimeseriesListItemAdded(timeseries)

    def onTimeseriesListItemAdded(self, timeseries: TimeseriesModel):
        view                        = TimeseriesView(timeseries, self._time_window)
        widget                      = QListWidgetItem()
        self._widgets[view]         = widget
        self.addItem(widget)
        self.setItemWidget(widget, view)
        widget.setSizeHint(view.minimumSizeHint())

    def onTimeseriesListItemRemoved(self, timeseries: TimeseriesModel):
        row = self._timeseries_row(timeseries)
        self.takeItem(row)

    def _timeseries_view(self, timeseries: TimeseriesModel) -> TimeseriesView:
        for view in self._widgets.keys():
            if view.timeseries is timeseries:
                return view
        raise ValueError("Not Found")

    def _timeseries_row(self, timeseries: TimeseriesModel) -> int:
        view    = self._timeseries_view(timeseries)
        widget  = self._widgets[view]
        for row in range(self.count()):
            if self.item(row) is widget:
                return row
        raise ValueError("Not Found")
