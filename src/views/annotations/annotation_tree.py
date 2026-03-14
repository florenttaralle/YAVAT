from __future__ import annotations

import json

from PyQt6.QtCore import QAbstractItemModel, QMimeData, QModelIndex, QItemSelectionModel, Qt
from PyQt6.QtWidgets import QHeaderView, QTreeView, QWidget, QAbstractItemView

from src.models.annotation import AnnotationModel, AnnotationGroupModel
from src.models.application_state import ApplicationStateModel

class AnnotationTreeModel(QAbstractItemModel):
    MIME_TYPE = "application/x-yavat-annotation-tree-item"

    def __init__(self, root: AnnotationGroupModel, parent: QWidget | None = None):
        QAbstractItemModel.__init__(self, parent)
        self._root = root

    @property
    def root(self) -> AnnotationGroupModel:
        return self._root

    def set_root(self, root: AnnotationGroupModel):
        self.beginResetModel()
        self._root = root
        self.endResetModel()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 2

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        parent_item = self._item_for_index(parent)
        if isinstance(parent_item, AnnotationGroupModel):
            return len(parent_item)
        return 0

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if row < 0 or column < 0 or column >= self.columnCount():
            return QModelIndex()

        parent_item = self._item_for_index(parent)
        if not isinstance(parent_item, AnnotationGroupModel):
            return QModelIndex()
        if row >= len(parent_item):
            return QModelIndex()

        child_item = parent_item[row]
        return self.createIndex(row, column, child_item)

    def parent(self, child: QModelIndex) -> QModelIndex:
        if not child.isValid():
            return QModelIndex()

        child_item = child.internalPointer()
        if child_item is None or child_item == self._root:
            return QModelIndex()

        parent_item, _ = self._find_parent(self._root, child_item)
        if parent_item is None or parent_item == self._root:
            return QModelIndex()

        grand_parent, parent_item_row = self._find_parent(self._root, parent_item)
        if grand_parent is None or parent_item_row < 0:
            return QModelIndex()

        return self.createIndex(parent_item_row, 0, parent_item)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        item = index.internalPointer()
        if index.column() == 0:
            return item.name
        return ""

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        return None # nothing in column headers, but we want the header so we can resize first column

    def _item_for_index(self, index: QModelIndex) -> AnnotationGroupModel | AnnotationModel:
        if not index.isValid():
            return self._root
        return index.internalPointer()

    def item_for_index(self, index: QModelIndex) -> AnnotationGroupModel | AnnotationModel | None:
        if not index.isValid():
            return None
        return index.internalPointer()

    def index_for_item(self, target: AnnotationModel, column: int = 0) -> QModelIndex:
        if target == self._root:
            return QModelIndex()
        return self._find_index(self._root, target, QModelIndex(), column)

    def _find_parent(
        self,
        parent_group: AnnotationGroupModel,
        target: AnnotationModel,
    ) -> tuple[AnnotationGroupModel | None, int]:
        for row in range(len(parent_group)):
            item = parent_group[row]
            if item == target:
                return parent_group, row
            if isinstance(item, AnnotationGroupModel):
                found_parent, found_row = self._find_parent(item, target)
                if found_parent is not None:
                    return found_parent, found_row
        return None, -1

    def flags(self, index):
        base = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.isValid():
            base |= Qt.ItemFlag.ItemIsDragEnabled # Drag -> move up/down
            item = index.internalPointer()
            if isinstance(item, AnnotationGroupModel):
                base |= Qt.ItemFlag.ItemIsDropEnabled # Drop -> put inside
        else:
            base |= Qt.ItemFlag.ItemIsDropEnabled  # root
        return base

    def supportedDragActions(self): return Qt.DropAction.MoveAction
    def supportedDropActions(self): return Qt.DropAction.MoveAction

    def mimeTypes(self) -> list[str]:
        return [self.MIME_TYPE]

    def mimeData(self, indexes: list[QModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        row_indexes = [index for index in indexes if index.isValid() and index.column() == 0]
        if len(row_indexes) != 1:
            return mime_data
        source_index = row_indexes[0]
        payload = {"path": self._index_path(source_index)}
        mime_data.setData(self.MIME_TYPE, json.dumps(payload).encode("utf-8"))
        return mime_data

    def dropMimeData(
        self,
        data: QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QModelIndex,
    ) -> bool:
        if action != Qt.DropAction.MoveAction:
            return False
        if not data.hasFormat(self.MIME_TYPE):
            return False

        try:
            payload = json.loads(bytes(data.data(self.MIME_TYPE)).decode("utf-8"))
            source_path = payload["path"]
        except Exception:
            return False

        source_parent_index = self._index_from_path(source_path[:-1])
        source_row = source_path[-1]

        if parent.isValid():
            drop_item = parent.internalPointer()
            if isinstance(drop_item, AnnotationGroupModel):
                destination_parent_index = parent
                destination_child = row if row >= 0 else len(drop_item)
            else:
                destination_parent_index = parent.parent()
                destination_child = row if row >= 0 else (parent.row() + 1)
        else:
            destination_parent_index = QModelIndex()
            destination_child = row if row >= 0 else len(self._root)

        return self.moveRows(source_parent_index, source_row, 1, destination_parent_index, destination_child)

    def moveRows(
        self,
        sourceParent: QModelIndex,
        sourceRow: int,
        count: int,
        destinationParent: QModelIndex,
        destinationChild: int,
    ) -> bool:
        if count != 1:
            return False

        source_parent = self._item_for_index(sourceParent)
        destination_parent = self._item_for_index(destinationParent)
        if not isinstance(source_parent, AnnotationGroupModel):
            return False
        if not isinstance(destination_parent, AnnotationGroupModel):
            return False
        if sourceRow < 0 or sourceRow >= len(source_parent):
            return False

        destination_child = max(0, min(destinationChild, len(destination_parent)))
        moving_item = source_parent[sourceRow]

        if isinstance(moving_item, AnnotationGroupModel) and self._contains_group(moving_item, destination_parent):
            return False

        if source_parent == destination_parent:
            if destination_child == sourceRow or destination_child == sourceRow + 1:
                return False

        self.beginMoveRows(sourceParent, sourceRow, sourceRow + count - 1, destinationParent, destination_child)

        source_parent._items.pop(sourceRow)
        final_pos = destination_child
        if source_parent == destination_parent and destination_child > sourceRow:
            final_pos -= 1
        destination_parent._items.insert(final_pos, moving_item)
        moving_item.setParent(destination_parent)

        if source_parent == destination_parent:
            source_parent.item_moved.emit(moving_item, sourceRow, final_pos)
        else:
            source_parent.item_detached.emit(moving_item, sourceRow)
            destination_parent.item_attached.emit(moving_item, final_pos)

        self.endMoveRows()
        return True

    def _find_index(
        self,
        parent_group: AnnotationGroupModel,
        target: AnnotationModel,
        parent_index: QModelIndex,
        column: int,
    ) -> QModelIndex:
        for row in range(len(parent_group)):
            item = parent_group[row]
            index = self.index(row, column, parent_index)
            if item == target:
                return index
            if isinstance(item, AnnotationGroupModel):
                child_match = self._find_index(item, target, index, column)
                if child_match.isValid():
                    return child_match
        return QModelIndex()

    def _contains_group(self, root_group: AnnotationGroupModel, target_group: AnnotationGroupModel) -> bool:
        if root_group == target_group:
            return True
        for row in range(len(root_group)):
            item = root_group[row]
            if isinstance(item, AnnotationGroupModel) and self._contains_group(item, target_group):
                return True
        return False

    def _index_path(self, index: QModelIndex) -> list[int]:
        path: list[int] = []
        current = index
        while current.isValid():
            path.append(current.row())
            current = current.parent()
        path.reverse()
        return path

    def _index_from_path(self, path: list[int]) -> QModelIndex:
        current = QModelIndex()
        for row in path:
            current = self.index(row, 0, current)
            if not current.isValid():
                return QModelIndex()
        return current


class AnnotationTreeView(QTreeView):
    def __init__(self, app_state: ApplicationStateModel, parent: QWidget | None = None):
        QTreeView.__init__(self, parent)
        self.app_state = app_state
        self._selection_sync_enabled = True
        self._selection_model: QItemSelectionModel | None = None
        self.setRootIsDecorated(True)
        self.setAllColumnsShowFocus(True)
        self._configure_columns()
        self._set_active_annotation(app_state.active_annotation)

        # allow item draw/drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        # set header height to minimum
        header = self.header()
        header.setFixedHeight(10)  # pick the height you want
        header.setStyleSheet("QHeaderView::section { padding: 0px; }")

    def _configure_columns(self):
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setColumnWidth(0, 260)

    def set_annotations(self, annotations: AnnotationGroupModel|None):
        if annotations is not None:
            model = AnnotationTreeModel(annotations, self)
        else:
            model = None
        self.setModel(model)
        if self._selection_model is not None:
            self._selection_model.currentChanged.disconnect(self.onCurrentChanged)
        self._selection_model = self.selectionModel()
        if self._selection_model is not None:
            self._selection_model.currentChanged.connect(self.onCurrentChanged)
        if model is not None:
            model.rowsMoved.connect(self.onRowsMoved)
        self._configure_columns()
        self.expandAll()
        self._sync_selection_with_active_item()

    def _set_active_annotation(self, active_annotation: AnnotationModel | None):
        if self.app_state.active_annotation is not None:
            self.app_state.watched_active_annotation.changed.disconnect(self.onActiveAnnotationChanged)
        self.app_state.set_active_annotation(active_annotation)
        if active_annotation is not None:
            self.app_state.watched_active_annotation.changed.connect(self.onActiveAnnotationChanged)
        self._sync_selection_with_active_item()

    def onCurrentChanged(self, current: QModelIndex, previous: QModelIndex):
        if (not self._selection_sync_enabled) or (self.self.app_state.active_annotation is None):
            return
        model = self.model()
        if model is None:
            return
        item = model.item_for_index(current)
        self.app_state.set_active_annotation(item)

    def onActiveAnnotationChanged(self, item: AnnotationModel | None):
        self._sync_selection_with_active_item(item)

    def onRowsMoved(self, *args):
        self._sync_selection_with_active_item()

    def _sync_selection_with_active_item(self, item: AnnotationModel | None = None):
        if self.app_state.active_annotation is None:
            return
        model = self.model()
        if model is None:
            return
        item = self.app_state.active_annotation if item is None else item
        self._selection_sync_enabled = False
        try:
            if item is None:
                self.clearSelection()
                self.setCurrentIndex(QModelIndex())
                return
            index = model.index_for_item(item, 0)
            if not index.isValid():
                self.clearSelection()
                self.setCurrentIndex(QModelIndex())
                return
            parent = model.parent(index)
            while parent.isValid():
                self.expand(parent)
                parent = model.parent(parent)
            self.setCurrentIndex(index)
            self.selectionModel().select(
                index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect
                | QItemSelectionModel.SelectionFlag.Rows,
            )
            self.scrollTo(index)
        finally:
            self._selection_sync_enabled = True
