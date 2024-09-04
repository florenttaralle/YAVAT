from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
# ##################################################################
from src.models.annotation_list import AnnotationListModel, AnnotationModel
from src.views.dialogs.editor_dialogs import exec_annotation_dialog
from src.icons import Icons
# ##################################################################

class AnnotationContextualMenu(QObject):
    def __init__(self, annotation: AnnotationModel, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._annotation = annotation
        
        self._act_edit = QAction(Icons.Edit.icon(), "Edit Annotation", self)
        self._act_edit.triggered.connect(self.onEdit)
        
        self._act_move_up = QAction(Icons.MoveUp.icon(), "Move Up", self)
        self._act_move_up.triggered.connect(self.onMoveUp)

        self._act_move_down = QAction(Icons.MoveDown.icon(), "Move Down", self)
        self._act_move_down.triggered.connect(self.onMoveDown)        

        self._act_remove = QAction(Icons.TimelineRem.icon(), "Delete Annotation", self)
        self._act_remove.triggered.connect(self.onRemove)

    def attach(self, menu: QMenu):
        menu.addAction(self._act_edit)
        menu.addAction(self._act_move_up)
        menu.addAction(self._act_move_down)
        menu.addAction(self._act_remove)
        return self
    
    def onEdit(self):
        exec_annotation_dialog(self._annotation)

    def onRemove(self):
        button = QMessageBox.warning(None, 
                                     "Delete Annotation", 
                                     f"About to delete annotation: '{self._annotation.name}'", 
                                     QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel, 
                                     QMessageBox.StandardButton.Cancel)
        if button == QMessageBox.StandardButton.Ok:
            annotations: AnnotationListModel = self._annotation.parent()
            annotations.remove(self._annotation)

    def onMoveUp(self):
        annotations: AnnotationListModel = self._annotation.parent()
        annotations.move_up(self._annotation)

    def onMoveDown(self):
        annotations: AnnotationListModel = self._annotation.parent()
        annotations.move_down(self._annotation)

