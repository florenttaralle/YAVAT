from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from enum import IntEnum
from typing import Mapping
from src.models.annotation_list import AnnotationListModel
from src.models.time_window import TimeWindowModel
from src.models.annotation import AnnotationModel
from src.models.timeseries import TimeseriesModel
from src.models.annotation_watchers import AnnotationWatcherSingleton, AnnotationNameWatcher, AnnotationValueWatcherModel
from src.icons import Icons
            
class ValueGridModel(QAbstractTableModel):
    class Column(IntEnum):
        Name    = 0
        Value   = 1
    
    def __init__(self, annotations: AnnotationListModel, time_window: TimeWindowModel, parent: QObject|None=None):
        QAbstractTableModel.__init__(self, parent)
        self._annotations       = annotations
        self._time_window       = time_window
        self._value_watchers:   Mapping[AnnotationModel, AnnotationValueWatcherModel] = {}
        self._name_watchers:    Mapping[AnnotationModel, AnnotationNameWatcher] = {}
        self._connect()

    def _connect(self):
        self._time_window.position_changed.connect(self.onTimeWindowPositionChanged)
        self._annotations.item_moved.connect(self.onAnnotationsItemMoved)
        for annotation in self._annotations:
            self.onAnnotationsItemAdded(annotation)
        self._annotations.item_added.connect(self.onAnnotationsItemAdded)
        self._annotations.item_removed.connect(self.onAnnotationsItemRemoved)

    def rowCount(self, index=None):
        return 1 + len(self._annotations)
    
    def columnCount(self, index=None):
        return len(self.Column)
    
    def headerData(self, section, orientation, role):
        if (role == Qt.ItemDataRole.DisplayRole) and (orientation == Qt.Orientation.Horizontal):
            match section:
                case 0:     return "Name"
                case _:     return "Value"

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        match role:
            case Qt.ItemDataRole.DisplayRole: # Values
                if index.row() == 0:
                    match index.column():
                        case 0: return "Frame Id"
                        case _: return self._time_window.position
                else:
                    annotation = self._annotations[index.row()-1]
                    match index.column():
                        case self.Column.Name:  return annotation.name
                        case self.Column.Value: 
                            value = self._value_watchers[annotation].value
                            if isinstance(value, str):      return f"'{value}'"
                            elif isinstance(value, float):  return round(value, 2)
                            else:                           return value

            case Qt.ItemDataRole.DecorationRole: # Icons
                if index.column() == self.Column.Name:
                    match index.row():
                        case 0:     return Icons.XValueClock.icon()
                        case _:     
                            annotation = self._annotations[index.row() - 1]
                            if isinstance(annotation, TimeseriesModel):
                                return Icons.YValueTS.icon()
                            else:
                                return Icons.YValueTL1.icon()

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        # prevent first row to be selected
        flags = Qt.ItemFlag.ItemNeverHasChildren | Qt.ItemFlag.ItemIsEnabled
        if index.row() > 0:
            flags |= Qt.ItemFlag.ItemIsSelectable
        return flags

    def onAnnotationsItemAdded(self, annotation: AnnotationModel):
        self.beginResetModel()
        self._value_watchers[annotation] = AnnotationWatcherSingleton.get_or_create(
            AnnotationValueWatcherModel, annotation, self._time_window)
        self._value_watchers[annotation].value_changed.connect(self.onAnnotationValueChanged)
        self._name_watchers[annotation] = AnnotationWatcherSingleton.get_or_create(
            AnnotationNameWatcher, annotation)
        self._name_watchers[annotation].name_changed.connect(self.onAnnotationNameChanged)
        self.endResetModel()

    def onAnnotationsItemRemoved(self, annotation: AnnotationModel):
        self.beginResetModel()
        annotation.name_changed.disconnect(self.onAnnotationNameChanged)
        self._value_watchers[annotation].value_changed.disconnect(self.onAnnotationValueChanged)
        del self._value_watchers[annotation]
        self._name_watchers[annotation].name_changed.disconnect(self.onAnnotationNameChanged)
        del self._name_watchers[annotation]
        self.endResetModel()

    def onAnnotationsItemMoved(self, annotation: AnnotationModel, prv_index: int, new_index: int):
        # update all annotation-related cells 
        self.dataChanged.emit(self.index(1, 0), self.index(self.rowCount() - 1, self.columnCount() - 1), [])

    def onTimeWindowPositionChanged(self, frame_id: int):
        # update frame_id cell
        self.dataChanged.emit(self.index(0, self.Column.Value), self.index(0, self.Column.Value), [Qt.ItemDataRole.DisplayRole])

    def onAnnotationNameChanged(self, annotation: AnnotationModel, name: str):
        # update annotation-related name cell
        row = self._annotations.index(annotation) + 1
        self.dataChanged.emit(self.index(row, self.Column.Name), self.index(row, self.Column.Name), [Qt.ItemDataRole.DisplayRole])

    def onAnnotationValueChanged(self, annotation: AnnotationModel, frame_id: int, value: object):
        # update annotation-related value cell
        row = self._annotations.index(annotation) + 1
        self.dataChanged.emit(self.index(row, self.Column.Value), self.index(row, self.Column.Value), [Qt.ItemDataRole.DisplayRole])
