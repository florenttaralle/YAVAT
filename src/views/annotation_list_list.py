import attr
from typing import List
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QAbstractItemView
from src.models.time_window import TimeWindowModel
from src.models.annotation_list import AnnotationListModel, AnnotationModel
from src.views.annotation import AnnotationView
from src.views.timeline import TimelineView, TimelineModel

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
        
        
    def set_context(self, time_window: TimeWindowModel|None, annotations: AnnotationListModel|None):
        if self._time_window is not None:
            self._annotations.selected_changed.disconnect(self.onModelSelectionChanged)
            self._annotations.item_added.disconnect(self.onAnnotationAdded)
            self._annotations.item_removed.disconnect(self.onAnnotationRemoved)
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
        self.setEnabled(self._time_window is not None)

    def onModelSelectionChanged(self, annotation: AnnotationModel|None):
        # Model -> View
        for item in self._items:
            item.widget.setSelected(item == annotation)

    def onSelectionChanged(self):
        # View -> Model
        selected_widgets = self.selectedItems()
        if len(selected_widgets):
            widget  = selected_widgets[0]
            item    = self._get_item(widget)
            annotation = item.annotation
        else:
            annotation = None
        self._annotations.set_selected(annotation)
    
    def _get_item(self, part) -> Item:
        return self._items[self._items.index(part)]

    def onAnnotationAdded(self, annotation: AnnotationModel):
        view    = self._view_factory(annotation)
        widget  = QListWidgetItem()
        item    = self.Item(annotation, view, widget)
        self._items.append(item)
        self.addItem(widget)
        self.setItemWidget(widget, view)
        widget.setSizeHint(view.minimumSizeHint())
        widget.setSelected(annotation.selected)
        # TODO connect to view signals ???
    
    def onAnnotationRemoved(self, annotation: AnnotationModel):
        item    = self._get_item(annotation)
        row     = self._item_row(item)
        self.takeItem(row)

    def _item_row(self, item: Item):
        for row in range(self.count()):
            if item == self.item(row):
                return row

    def _view_factory(self, annotation: AnnotationModel) -> AnnotationView:
        if isinstance(annotation, TimelineModel):
            return TimelineView(annotation, self._time_window)
    