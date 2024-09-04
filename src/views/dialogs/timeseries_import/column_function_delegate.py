from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from .column import Column, ColumnFunction


class ColumnFunctionDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        column: Column  = index.model().data(index, Qt.ItemDataRole.UserRole)
        if column.usable:
            if isinstance(self.parent(), QAbstractItemView):
                self.parent().openPersistentEditor(index)
            QStyledItemDelegate.paint(self, painter, option, index)
        else:
            option.text = ""
            QApplication.style().drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        editor = QComboBox(parent)
        column = index.model().data(index, Qt.ItemDataRole.UserRole)
        for cfunction in column.cfunctions:
            editor.addItem(cfunction.name, cfunction)
        editor.setCurrentIndex(editor.findData(column.cfunction))
        editor.currentIndexChanged.connect(lambda _: self.commitData.emit(editor))
        return editor

    def setEditorData(self, editor, index):
        # model -> view
        column  = index.model().data(index, Qt.ItemDataRole.UserRole)
        index   = editor.findData(column.cfunction)
        editor.setCurrentIndex(index)

    def setModelData(self, editor, model, index):
        # view -> model
        model.setData(index, editor.currentData(), Qt.ItemDataRole.UserRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

