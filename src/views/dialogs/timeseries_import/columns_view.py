from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from typing import List
from .columns_model import ColumnsModel
from .column_function_delegate import ColumnFunctionDelegate

class ColumnsView(QTableView):
    def __init__(self, columns: ColumnsModel, parent: QWidget|None=None):
        QTableView.__init__(self, parent)
        self._proxy = QSortFilterProxyModel()
        self._proxy.setDynamicSortFilter(False)
        self._proxy.setSourceModel(columns)
        self.setModel(self._proxy)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(True)
        self.setItemDelegateForColumn(0, ColumnFunctionDelegate(self))
        self.setAlternatingRowColors(True)
        self._proxy.sort(1) # sort on the Id column, not the Function

    def dataChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: List[Qt.ItemDataRole]):
        if (topLeft == bottomRight) and (topLeft.column() == 0):
            self.updateRow(topLeft.row())

    def updateRow(self, row: int):
        for cid in range(self.model().columnCount()):
            self.update(self.model().index(row, cid))
