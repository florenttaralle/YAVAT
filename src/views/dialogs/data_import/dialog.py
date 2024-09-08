from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import os, itertools as it
import pandas as pd, numpy as np
from typing import Mapping
from src.models.yavat import YavatModel
from src.models.timeseries import TimeseriesModel
from src.models.timeline import TimelineModel, EventModel
from src.icons import Icons
from src.models.profile import ProfileModel
from .columns_model import ColumnsModel, Column
from .column_function import ColumnFunction
from .columns_view import ColumnsView

class DataImportDialog(QDialog):
    def __init__(self, df: pd.DataFrame, yavat: YavatModel, 
                 profile: ProfileModel|None=None, parent: QWidget|None=None):
        QDialog.__init__(self, parent)
        self.setMinimumWidth(1200)
        self.setMinimumHeight(600)
        self._df        = df
        self._yavat     = yavat
        self._profile   = profile
        self.setWindowTitle("Import Annotations")
        self.setModal(True)
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(10)

        self._info_label    = QLabel()
        self._info_label.setTextFormat(Qt.TextFormat.RichText)
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        n_rows = len(df.iloc[:,0])
        n_cols = len(df.columns)
        self._info_label.setText(f"""
        <html>
            The data you provided contains {n_rows} rows and {n_cols} columns. <br>
            You must select <strong>exactly one</strong> column to be used either as frame_id or timestamp (x axis). <br>
            You must select <strong>at least one</strong> column to bu used a new timeseries (y axis). <br>
            You can import multiple annotations at once. <br>
            You can change the name of the columns you want to import. <br>
            You can change the range (min, max) of the columns you want to import (with min  max).
        </html>
        """)
        
        self.layout().addWidget(self._info_label)
        
        self._columns       = ColumnsModel(df)
        self._columns_view  = ColumnsView(self._columns)
        self.layout().addWidget(self._columns_view)

        self._msgs          = QStandardItemModel(self)
        self._msg_list      = QListView()
        self._msg_list.setModel(self._msgs)
        self._msg_list.setMaximumHeight(60)
        self.layout().addWidget(self._msg_list)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        self.layout().addWidget(self._buttons)
        
        self._columns.dataChanged.connect(self.onColumnsChanged)
        self._update()

    def onColumnsChanged(self, *_):
        self._update()

    def _get_columns(self):
        x_columns = [
            column
            for column in self._columns._columns
            if column.cfunction.is_x_value
        ]
        y_columns = [
            column
            for column in self._columns._columns
            if column.cfunction.is_y_value
        ]
        return x_columns, y_columns

    @property
    def ok_button(self) -> QPushButton:
        return self._buttons.button(QDialogButtonBox.StandardButton.Ok)

    def _update(self):
        x_cols, y_cols = self._get_columns()
        self._msgs.clear()
        valid = True
        if len(x_cols) < 1:
            self._msgs.appendRow(QStandardItem(Icons.MessageWarning.icon(), "No XValue (FrameId or Timestamp) selected."))
            valid = False
        elif len(x_cols) > 1:
            self._msgs.appendRow(QStandardItem(Icons.MessageWarning.icon(), "More than one XValue (FrameId or Timestamp) selected."))
            valid = False
        if len(y_cols) < 1:
            self._msgs.appendRow(QStandardItem(Icons.MessageWarning.icon(), "No YValue selected."))
            valid = False
        for column in y_cols:
            if (column.min is not None) and (column.min > column.max):
                self._msgs.appendRow(QStandardItem(Icons.MessageWarning.icon(), f"Invalid range {column.min} > {column.max} for column {column.name}."))
                valid = False
        self.ok_button.setEnabled(valid)

    def _format_x_values(self, column: Column):
        match column.cfunction:
            case ColumnFunction.FrameId:        return column.series
            case ColumnFunction.Timestamp:      return column.series.apply(lambda ts: ts.total_seconds() / self._yavat.video.fps)
            case ColumnFunction.TimestampS:     return column.series.apply(lambda ts: ts / self._yavat.video.fps)
            case ColumnFunction.TimestampMS:    return column.series.apply(lambda ts: ts / (1000 * self._yavat.video.fps))

    def exec(self) -> bool:
        status = QDialog.exec(self)
        if status == QDialog.DialogCode.Accepted:
            x_cols, y_cols  = self._get_columns()
            if self._yavat is None:
                # for test/debug purpose
                print(f"x:{x_cols}, y:{y_cols}")
            else:
                x_values = self._format_x_values(x_cols[0]).values
                for column in y_cols:
                    y_values = column.series.values
                    match column.cfunction:
                        case ColumnFunction.Timeseries:
                            timeseries = TimeseriesModel(self._yavat.video.n_frames, 
                                                        zip(x_values, y_values),
                                                        column.min, column.max,
                                                        column.name)
                            if self._profile is not None:
                                self._profile.update_annotation(timeseries)
                            self._yavat.annotations.append(timeseries)

                        case ColumnFunction.TimelineSingle:
                            timeline = TimelineModel(self._yavat.video.n_frames, column.name)
                            for y_value, first, last in self._group_values(x_values, y_values):
                                timeline.add(EventModel(first, last, label=str(y_value)))
                            self._yavat.annotations.append(timeline)
                        
                        case ColumnFunction.TimelineMulti:
                            timelines: Mapping[str, TimelineModel] = {}
                            for y_value, first, last in self._group_values(x_values, y_values):
                                timeline_name = f"{column.name} - {y_value}"
                                if timeline_name not in timelines:
                                    timelines[timeline_name] = TimelineModel(self._yavat.video.n_frames, timeline_name)
                                timelines[timeline_name].add(EventModel(first, last))
                            for timeline in timelines.values():
                                if self._profile is not None:
                                    self._profile.update_annotation(timeline)
                                self._yavat.annotations.append(timeline)

                return True
        return False

    def _group_values(self, x_values: np.ndarray, y_values: np.ndarray, sparse_x: bool=False):
        groups      = [] # [(y_value, first, last), ...]
        frame_ids   = x_values.round().astype(int)
        for y_value, group in it.groupby(zip(frame_ids, y_values), key=lambda xy: xy[1]):
            X, _    = zip(*group)
            if sparse_x:
                # continuous X not required
                groups.append([y_value, int(min(X)), int(max(X))])
            else:
                # continuous X required
                groups.append([y_value, int(X[0]), int(X[0])])
                for x in X[1:]:
                    if x == groups[-1][2] + 1:
                        groups[-1][2] = int(x)
        return groups

    @classmethod
    def import_from_file(cls, yavat: YavatModel, profile: ProfileModel|None=None, parent: QWidget|None=None) -> bool:
        # pick the file
        CSV_EXT     = [".csv", ".txt"]
        JSON_EXT    = [".json"]
        EXCEL_EXT   = [".xls", ".xlsx"]
        ext_list    = lambda exts: " ".join(["*" + ext for ext in exts])
        filename,  _ = QFileDialog.getOpenFileName(None, "Load Timeseries annotations",
                                                    os.path.dirname(yavat.video.path), 
                                                    ";;".join([
                                                        "CSV ({ext})".format(ext=ext_list(CSV_EXT)),
                                                        "JSON ({ext})".format(ext=ext_list(JSON_EXT)),
                                                        "Excel ({ext})".format(ext=ext_list(EXCEL_EXT)),
                                                        "All (*)"
                                                    ]))
        if not filename:
            return False
        
        # parse the file
        error = None
        try:
            ext = os.path.splitext(filename)[1]
            if ext in CSV_EXT:
                df = pd.read_csv(filename)
            elif ext in JSON_EXT:
                df = pd.read_json(filename)
            elif ext in EXCEL_EXT:
                df = pd.read_excel(filename)
            else:
                raise Exception(f"Unknown file extension: {ext}")
        except Exception as what:
            error = str(what)
        
        # pick dialog
        if not error:
            try:
                return cls(df, yavat, profile, parent).exec()
            except Exception as what:
                error = str(what)
        QMessageBox.warning(None, "Error Importing Timeseries", error, 
                            QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
