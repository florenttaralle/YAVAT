from __future__ import annotations
from PyQt6.QtGui import QColor, QColorConstants
from enum import IntEnum, auto
from typing import List
import numpy as np


class ColumnFunction(IntEnum):
    NotApplicable   = auto()
    Ignored         = auto()
    # X-Values
    FrameId         = auto()
    Timestamp       = auto()
    TimestampS      = auto()
    TimestampMS     = auto()
    # Y-Values
    Timeseries      = auto()    # single timeseries
    TimelineSingle  = auto()    # single timeline : values -> event label
    TimelineMulti   = auto()    # multiple timeline : values -> select the timeline

    _TIMELINE_MULTI_MAX_COUNT = 10

    @property
    def used(self) -> bool:
        return self not in {ColumnFunction.NotApplicable, ColumnFunction.Ignored}

    @property
    def is_x_value(self) -> bool:
        return self in {ColumnFunction.FrameId, ColumnFunction.Timestamp, ColumnFunction.TimestampS, ColumnFunction.TimestampMS}

    @property
    def is_y_value(self) -> bool:
        return self in {ColumnFunction.Timeseries, ColumnFunction.TimelineSingle, ColumnFunction.TimelineMulti}

    def is_applicable(self, dtype, n_values: int) -> bool:
        match self:
            case ColumnFunction.FrameId:        return np.issubdtype(dtype, np.number) and not np.issubdtype(dtype, np.timedelta64)
            case ColumnFunction.TimestampS:     return np.issubdtype(dtype, np.number)
            case ColumnFunction.TimestampMS:    return np.issubdtype(dtype, np.number)
            case ColumnFunction.Timestamp:      return np.issubdtype(dtype, np.timedelta64)
            case ColumnFunction.Timeseries:     return np.issubdtype(dtype, np.number) and not np.issubdtype(dtype, np.timedelta64)
            case ColumnFunction.TimelineSingle: return not np.issubdtype(dtype, np.number) # str
            case ColumnFunction.TimelineMulti:  return (n_values <= self._TIMELINE_MULTI_MAX_COUNT)
        return False

    @staticmethod
    def applicable_functions(dtype, n_values: int) -> List[ColumnFunction]:
        applicable_functions = [
            cfunction
            for cfunction in ColumnFunction
            if cfunction.used and cfunction.is_applicable(dtype, n_values)
        ]
        if len(applicable_functions):
            applicable_functions.append(ColumnFunction.Ignored)
        return applicable_functions
    
    @property
    def color(self) -> QColor:
        if self.is_x_value:
            return QColorConstants.Blue
        elif self.is_y_value:
            return QColorConstants.DarkGreen
