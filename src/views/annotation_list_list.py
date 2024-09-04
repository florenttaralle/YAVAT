import attr, json
from typing import List
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from src.models.time_window import TimeWindowModel
from src.models.annotation_list import AnnotationListModel, AnnotationModel
from src.views.annotation import AnnotationView
from src.views.timeline import TimelineView, TimelineModel
from src.views.timeseries import TimeseriesView, TimeseriesModel

class AnnotationListListView(QListWidget):
    @attr.define
    class Item:
        annotation: AnnotationModel
        view:       AnnotationView
        widget:     QListWidgetItem
        
        def __eq__(self, value) -> bool:
            return (value == self.annotation) or (value == self.view) or (value == self.widget)
    
    def __init__(self, time_window: TimeWindowModel|None=None, annotations: AnnotationListModel|None=None, parent: QWidget|None=None):
        QListWidget.__init__(self, parent)
        self._time_window:  TimeWindowModel|None=None
        self._annotations:  AnnotationListModel|None=None
        self._items:        List[self.Item] = [] 
        selected_color = self.palette().highlight().color().name()
        self.setStyleSheet(f"""
            QListWidget {{
                border: 0px;
            }}
            QListWidget::item::selected {{ 
                background: transparent; 
                border: 1px solid {selected_color};
                border-left: 10px solid {selected_color};
            }}
        """)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.itemSelectionChanged.connect(self.onSelectionChanged)
        self.set_context(time_window, annotations)
        self.setDragDropMode(QListView.DragDropMode.DragDrop)
    
    def mimeData(self, items: List[QListWidgetItem]) -> QMimeData:
        # prepare data type & content
        # get 'application/x-qabstractitemmodeldatalist' to allow item move behavior
        mime_data = QListWidget.mimeData(self, items)
        # this allow to export annotation content as JSON text via drag-n-drop
        data = [self._get_item(item).annotation.data() for item in items]
        if len(data) == 1:
            data = data[0]
        json_data = json.dumps(data, indent=2)
        mime_data.setText(json_data)        
        return mime_data

    def startDrag(self, actions: Qt.DropAction):
        # allow only copy (not move)
        QListWidget.startDrag(self, Qt.DropAction.CopyAction)

    def dropEvent(self, event: QDropEvent|None):
        # allow move item up/down in the list using drap-n-drop
        event.ignore()
        if (event.source() != self): return
        row = self.indexAt(event.position().toPoint()).row()
        self._annotations.move(self._annotations.selected, row)

    def set_context(self, time_window: TimeWindowModel|None, annotations: AnnotationListModel|None):
        if self._time_window is not None:
            self._annotations.selected_changed.disconnect(self.onModelSelectionChanged)
            self._annotations.item_added.disconnect(self.onAnnotationAdded)
            self._annotations.item_removed.disconnect(self.onAnnotationRemoved)
            self._annotations.item_moved.disconnect(self.onAnnotationMoved)
            self._items.clear()
            self.clear()
        self._time_window = time_window
        self._annotations = annotations
        if self._time_window is not None:
            for annotation in self._annotations:
                self.onAnnotationAdded(annotation)
            self._annotations.selected_changed.connect(self.onModelSelectionChanged)
            self._annotations.item_added.connect(self.onAnnotationAdded)
            self._annotations.item_removed.connect(self.onAnnotationRemoved)
            self._annotations.item_moved.connect(self.onAnnotationMoved)
        self.setEnabled(self._time_window is not None)

    def onModelSelectionChanged(self, annotation: AnnotationModel|None):
        # Model -> View
        if annotation is not None:
            item = self._get_item(annotation)
            item.widget.setSelected(True)
        else:
            self.clearSelection()

    def onSelectionChanged(self):
        # View -> Model
        selected_widgets = self.selectedItems()
        if len(selected_widgets):
            widget      = selected_widgets[0]
            item        = self._get_item(widget)
            annotation  = item.annotation
        else:
            annotation  = None
        self._annotations.set_selected(annotation)
    
    def _get_item(self, part) -> Item:
        return self._items[self._items.index(part)]

    def onAnnotationAdded(self, annotation: AnnotationModel):
        row     = self._annotations.index(annotation)
        widget  = QListWidgetItem()
        view    = self._view_factory(annotation)
        item    = self.Item(annotation, view, widget)
        self._items.append(item)
        self.insertItem(row, widget)
        self.setItemWidget(widget, view)
        widget.setSizeHint(view.minimumSizeHint())
        widget.setSelected(annotation.selected)
        widget.setHidden(not annotation.visible)
    
    def onAnnotationMoved(self, annotation: AnnotationModel, prv_index: int, new_index: int):
        self.onAnnotationRemoved(annotation)
        self.onAnnotationAdded(annotation)
        annotation.set_selected(True)
        item = self._get_item(annotation)
        item.view.setFocus()
    
    def onAnnotationRemoved(self, annotation: AnnotationModel):
        item    = self._get_item(annotation)
        row     = self._item_row(item)
        self.takeItem(row)
        self._items.remove(item)

    def _item_row(self, item: Item):
        return self.row(item.widget)

    def _view_factory(self, annotation: AnnotationModel, parent: QWidget|None=None) -> AnnotationView:
        if isinstance(annotation, TimelineModel):
            return TimelineView(annotation, self._time_window, parent=parent)
        elif isinstance(annotation, TimeseriesModel):
            return TimeseriesView(annotation, self._time_window, parent=parent)

