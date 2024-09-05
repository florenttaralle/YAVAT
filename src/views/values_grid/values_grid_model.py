from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from src.models.annotation_list import AnnotationListModel
from src.models.time_window import TimeWindowModel
from src.models.annotation import AnnotationModel
from src.models.timeseries import TimeseriesModel
from src.models.timeline import TimelineModel
from src.icons import Icons

class ValueGridModel(QAbstractTableModel):    
    def __init__(self, annotations: AnnotationListModel, time_window: TimeWindowModel, parent: QObject|None=None):
        QAbstractTableModel.__init__(self, parent)
        self._annotations = annotations
        self._time_window = time_window

        # update all values on position changed (values only) 
        self._time_window.position_changed.connect(
            lambda *_: self.dataChanged.emit(
                self.index(0, 1), 
                self.index(self.rowCount() - 1, 1), 
                []))

        annotations.item_moved.connect(self.onAnnotationsItemMoved)
        annotations.item_added.connect(self.onAnnotationsItemAdded)
        annotations.item_removed.connect(self.onAnnotationsItemRemoved)

    def rowCount(self, index=None):
        return 1 + len(self._annotations)
    
    def columnCount(self, index=None):
        return 2
    
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
                        case 0: return annotation.name
                        case _: return self._crt_value(annotation)

            case Qt.ItemDataRole.DecorationRole: # Icons
                if index.column() != 0: return None
                match index.row():
                    case 0:     return Icons.XValueClock.icon()
                    case _:     
                        annotation = self._annotations[index.row()-1]
                        if isinstance(annotation, TimeseriesModel):
                            return Icons.YValueTS.icon()
                        else:
                            return Icons.YValueTL1.icon()

    def _crt_value(self, annotation: AnnotationModel):
        if isinstance(annotation, TimelineModel):
            event = annotation.at_frame_id(self._time_window.position)
            return event.label if event else ""
        elif isinstance(annotation, TimeseriesModel):
            idx = annotation.X.index(self._time_window.position)
            return round(annotation.Y[idx], 2) if idx != 1 else None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        # prevent first row to be selected
        flags = Qt.ItemFlag.ItemNeverHasChildren | Qt.ItemFlag.ItemIsEnabled
        if index.row() > 0:
            flags |= Qt.ItemFlag.ItemIsSelectable
        return flags

    def onAnnotationsItemAdded(self, annotation: AnnotationModel):
        self.beginResetModel()
        self.endResetModel()

    def onAnnotationsItemRemoved(self, annotation: AnnotationModel):
        self.beginResetModel()
        self.endResetModel()

    def onAnnotationsItemMoved(self, annotation: AnnotationModel, prv_index: int, new_index: int):
        self.beginResetModel()
        self.endResetModel()
