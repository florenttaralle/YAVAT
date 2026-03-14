from __future__ import annotations

import json

from PyQt6.QtCore import QAbstractItemModel, QEvent, QMimeData, QModelIndex, QItemSelectionModel, QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QHeaderView, QTreeView, QWidget, QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem

from src.models.annotation import AnnotationModel, AnnotationGroupModel, TimelineModel, TimeseriesModel
from src.models.application_state import ApplicationStateModel
from src.icons import Icons
from .graph import graph_view_factory


class AnnotationNameDelegate(QStyledItemDelegate):
    color_icon_clicked = pyqtSignal(object)
    "SIGNAL: color_icon_clicked(annotation: AnnotationModel)"

    COLOR_BOX_MARGIN = 6

    def _color_box_size(self, option: QStyleOptionViewItem) -> int:
        # Keep the square tied to current row font size (reacts to global app font changes).
        return max(8, option.fontMetrics.height() - 2)

    def _text_rect(self, option: QStyleOptionViewItem) -> QRect:
        # Keep editable text zone away from left icon and right color swatch.
        color_box_size = self._color_box_size(option)
        right_reserve = color_box_size + (2 * self.COLOR_BOX_MARGIN)

        left_reserve = 0
        if option.features & QStyleOptionViewItem.ViewItemFeature.HasDecoration:
            left_reserve = option.decorationSize.width() + self.COLOR_BOX_MARGIN

        rect = QRect(option.rect)
        rect.adjust(left_reserve, 0, -right_reserve, 0)
        return rect

    def _color_rect(self, option: QStyleOptionViewItem) -> QRect:
        color_box_size = self._color_box_size(option)
        x = option.rect.right() - self.COLOR_BOX_MARGIN - color_box_size
        y = option.rect.top() + (option.rect.height() - color_box_size) // 2
        return QRect(x, y, color_box_size, color_box_size)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        if index.column() != 0:
            QStyledItemDelegate.paint(self, painter, option, index)
            return

        option_no_color = QStyleOptionViewItem(option)
        color_box_size = self._color_box_size(option)
        option_no_color.rect = self._text_rect(option)
        QStyledItemDelegate.paint(self, painter, option_no_color, index)

        item = index.internalPointer()
        color = getattr(item, "color", None)
        if color is None:
            return

        color_rect = self._color_rect(option)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(QPen(option.palette.mid().color()))
        painter.setBrush(color)
        painter.drawRect(color_rect)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if index.column() != 0:
            return QStyledItemDelegate.editorEvent(self, event, model, option, index)
        if (
            event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
        ):
            pos = event.position().toPoint()
            if self._color_rect(option).contains(pos):
                self.color_icon_clicked.emit(index.internalPointer())
                return True
        if event.type() == QEvent.Type.MouseButtonDblClick:
            pos = event.position().toPoint()
            if not self._text_rect(option).contains(pos):
                # Consume double-click on icon/swatch zones to prevent edit.
                return True
        return QStyledItemDelegate.editorEvent(self, event, model, option, index)

    def updateEditorGeometry(self, editor, option, index):
        if index.column() == 0:
            editor.setGeometry(self._text_rect(option))
            return
        QStyledItemDelegate.updateEditorGeometry(self, editor, option, index)


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

        item = index.internalPointer()
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if index.column() == 0:
                return item.name
            return ""

        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            if isinstance(item, AnnotationGroupModel):
                return Icons.MenuV.icon()
            if isinstance(item, TimelineModel):
                return Icons.Timeline.icon()
            if isinstance(item, TimeseriesModel):
                return Icons.Timeseries.icon()

        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole):
        if role != Qt.ItemDataRole.EditRole:
            return False
        if not index.isValid() or index.column() != 0:
            return False
        new_name = str(value).strip()
        if not new_name:
            return False
        item = index.internalPointer()
        if new_name == item.name:
            return False
        item.set_name(new_name)
        self.dataChanged.emit(
            index,
            index,
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole],
        )
        return True

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
            if index.column() == 0:
                base |= Qt.ItemFlag.ItemIsEditable
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
    color_icon_clicked = pyqtSignal(object)
    "SIGNAL: color_icon_clicked(annotation: AnnotationModel)"

    def __init__(self, app_state: ApplicationStateModel, parent: QWidget | None = None):
        QTreeView.__init__(self, parent)
        self.app_state = app_state
        self._selection_sync_enabled = True
        self._selection_model: QItemSelectionModel | None = None
        self._graph_views: dict[AnnotationModel, QWidget] = {}
        self.setRootIsDecorated(True)
        self.setAllColumnsShowFocus(True)
        self._name_delegate = AnnotationNameDelegate(self)
        self._name_delegate.color_icon_clicked.connect(self.onColorIconClicked)
        self.setItemDelegateForColumn(0, self._name_delegate)
        self._update_icon_size_from_font()
        self._configure_columns()

        # allow item draw/drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )

        # set header height to minimum
        header = self.header()
        header.setFixedHeight(10)  # pick the height you want
        header.setStyleSheet("QHeaderView::section { padding: 0px; }")

        self.app_state.watched_active_annotation.changed.connect(self.onActiveAnnotationChanged)
        self.app_state.watched_time_window.changed.connect(self.onTimeWindowChanged)

    def _update_icon_size_from_font(self):
        side = max(8, self.fontMetrics().height() - 2)
        self.setIconSize(QSize(side, side))

    def changeEvent(self, event):
        QTreeView.changeEvent(self, event)
        if event.type() == QEvent.Type.FontChange:
            self._update_icon_size_from_font()
            self.viewport().update()

    def _configure_columns(self):
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setColumnWidth(0, 260)

    def set_annotations(self, annotations: AnnotationGroupModel|None):
        self._clear_graph_views()
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
        self._refresh_graph_widgets()
        self._sync_selection_with_active_item()

    def onCurrentChanged(self, current: QModelIndex, previous: QModelIndex):
        if not self._selection_sync_enabled:
            return
        model = self.model()
        if model is None:
            return
        item = model.item_for_index(current)
        self.app_state.set_active_annotation(item)

    def onActiveAnnotationChanged(self, item: AnnotationModel | None):
        self._sync_selection_with_active_item(item)

    def onRowsMoved(self, *args):
        self._refresh_graph_widgets()
        self._sync_selection_with_active_item()

    def onTimeWindowChanged(self, time_window):
        self._refresh_graph_widgets()

    def onColorIconClicked(self, annotation: AnnotationModel):
        self.color_icon_clicked.emit(annotation)

    def _sync_selection_with_active_item(self, item: AnnotationModel | None = None):
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

    def _clear_graph_views(self):
        for graph_view in self._graph_views.values():
            graph_view.setParent(None)
            graph_view.deleteLater()
        self._graph_views.clear()

    def _refresh_graph_widgets(self):
        model = self.model()
        time_window = self.app_state.time_window
        if model is None:
            self._clear_graph_views()
            return
        if time_window is None:
            self._clear_graph_views()
            return

        valid_annotations: set[AnnotationModel] = set()

        def recurse(parent: QModelIndex):
            for row in range(model.rowCount(parent)):
                idx0 = model.index(row, 0, parent)
                idx1 = model.index(row, 1, parent)
                item = model.item_for_index(idx0)
                valid_annotations.add(item)
                graph_view = self._graph_views.get(item)
                if graph_view is None:
                    graph_view = graph_view_factory(item, time_window, self)
                    if graph_view is not None:
                        self._graph_views[item] = graph_view
                if graph_view is not None:
                    graph_view.setMinimumHeight(self.app_state.config.annotation_graph_height)
                    self.setIndexWidget(idx1, graph_view)
                recurse(idx0)

        recurse(QModelIndex())

        stale = [annotation for annotation in self._graph_views if annotation not in valid_annotations]
        for annotation in stale:
            graph_view = self._graph_views.pop(annotation)
            graph_view.setParent(None)
            graph_view.deleteLater()
