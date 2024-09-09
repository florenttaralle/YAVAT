from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import pandas as pd, numpy as np
from enum import IntEnum, auto
from datetime import timedelta
from .column import Column


class ModelColumn(IntEnum):
    Function    = 0
    Id          = auto()
    Name        = auto()
    Type        = auto()
    NbDistinct  = auto()
    Example     = auto()
    Min         = auto()
    Max         = auto()

EDITABLE_COLUMNS = {ModelColumn.Function, ModelColumn.Name, ModelColumn.Min, ModelColumn.Max}

class ColumnsModel(QAbstractTableModel):    
    def __init__(self, df: pd.DataFrame, parent: QObject|None=None):
        QAbstractTableModel.__init__(self, parent)
        self._df = df
        self._columns = [
            Column(
                id,
                df[name],
                name,
                df[name].iloc[0],
                df[name].min() if np.issubdtype(df[name].dtype, np.number) else None,
                df[name].max() if np.issubdtype(df[name].dtype, np.number) else None,
                len(df[name].value_counts())
            )
            for id, name in enumerate(df.columns)
        ]
        
    def rowCount(self, index=None):
        return len(self._columns)

    def columnCount(self, index=None):
        return len(ModelColumn)
    
    def headerData(self, section, orientation, role):
        if (role == Qt.ItemDataRole.DisplayRole) and (orientation == Qt.Orientation.Horizontal):
            match section:
                case ModelColumn.Function:      return "Function"
                case ModelColumn.Id:            return "Id"
                case ModelColumn.Name:          return "Name"
                case ModelColumn.Type:          return "Type"
                case ModelColumn.NbDistinct:    return "#Distinct"
                case ModelColumn.Example:       return "Example"
                case ModelColumn.Min:           return "Min"
                case ModelColumn.Max:           return "Max"

    def _str_value(self, value) -> str|None:
        if value is None:                       return None
        elif isinstance(value, timedelta):      return timedelta.__str__(value)
        elif isinstance(value, np.floating):    return str(np.round(value, 2))
        else:                                   return str(value)
        
    def _dtype_name(self, dtype) -> str:
        if dtype == object:     return "str"
        else:                   return dtype.name

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        column = self._columns[index.row()]
        match role:
            case Qt.ItemDataRole.UserRole:
                match index.column():
                    case ModelColumn.Function: return column

            case Qt.ItemDataRole.DisplayRole:
                match index.column():
                    case ModelColumn.Function:      return f"{int(not column.used)}-{column.cfunction.name}" 
                    case ModelColumn.Id:            return column.id
                    case ModelColumn.Name:          return column.name
                    case ModelColumn.Type:          return self._dtype_name(column.dtype)
                    case ModelColumn.NbDistinct:    return column.nb_values
                    case ModelColumn.Example:       return self._str_value(column.example)
                    case ModelColumn.Min:           return self._str_value(column.min)
                    case ModelColumn.Max:           return self._str_value(column.max)

            case Qt.ItemDataRole.BackgroundRole:
                color = column.cfunction.color
                if color is not None:
                    color.setAlphaF(.2)
                return color
            
            case Qt.ItemDataRole.EditRole:
                match index.column():
                    case ModelColumn.Name:      return column.name
                    case ModelColumn.Min:       return self._str_value(column.min)
                    case ModelColumn.Max:       return self._str_value(column.max)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = Qt.ItemFlag.ItemNeverHasChildren
        if self._columns[index.row()].usable:
            flags |= Qt.ItemFlag.ItemIsEnabled
            if index.column() in EDITABLE_COLUMNS:
                flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole) -> bool:
        column = self._columns[index.row()]
        match role:
            case Qt.ItemDataRole.UserRole:
                match index.column():
                    case ModelColumn.Function: 
                        column.cfunction = value
                        self.dataChanged.emit(index, index, [role])
                        return True
            case Qt.ItemDataRole.EditRole:
                match index.column():
                    case ModelColumn.Name:
                        column.name = str(value)
                        self.dataChanged.emit(index, index, [role])
                        return True
                    case ModelColumn.Min:
                        if column.set_min(value):
                            self.dataChanged.emit(index, index, [role])
                            return True
                    case ModelColumn.Max:
                        if column.set_max(value):
                            self.dataChanged.emit(index, index, [role])
                            return True
        return False
