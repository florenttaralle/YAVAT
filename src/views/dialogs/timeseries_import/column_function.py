from __future__ import annotations
from PyQt6.QtGui import QColor, QColorConstants
from enum import IntEnum, auto
from typing import List
import numpy as np


class ColumnFunction(IntEnum):
    NotApplicable   = auto()
    Ignored         = auto()
    FrameId         = auto()
    Timestamp       = auto()
    TimestampS      = auto()
    TimestampMS     = auto()
    YValue          = auto()

    @property
    def used(self) -> bool:
        return self not in {ColumnFunction.NotApplicable, ColumnFunction.Ignored}

    @property
    def is_timestamp(self) -> bool:
        return self in {
            ColumnFunction.FrameId, 
            ColumnFunction.Timestamp, 
            ColumnFunction.TimestampS, 
            ColumnFunction.TimestampMS}

    def is_applicable(self, dtype) -> bool:
        match self:
            case ColumnFunction.FrameId:        return np.issubdtype(dtype, np.number) and not np.issubdtype(dtype, np.timedelta64)
            case ColumnFunction.TimestampS:     return np.issubdtype(dtype, np.number)
            case ColumnFunction.TimestampMS:    return np.issubdtype(dtype, np.number)
            case ColumnFunction.Timestamp:      return np.issubdtype(dtype, np.timedelta64)
            case ColumnFunction.YValue:         return np.issubdtype(dtype, np.number) and not np.issubdtype(dtype, np.timedelta64)
        return False

    @staticmethod
    def applicable_functions(dtype) -> List[ColumnFunction]:
        applicable_functions = [
            cfunction
            for cfunction in ColumnFunction
            if cfunction.used and cfunction.is_applicable(dtype)
        ]
        if len(applicable_functions):
            applicable_functions.append(ColumnFunction.Ignored)
        return applicable_functions
    
    @property
    def color(self) -> QColor:
        match self:
            case ColumnFunction.FrameId:        return QColorConstants.Blue
            case ColumnFunction.Timestamp:      return QColorConstants.Blue
            case ColumnFunction.TimestampS:     return QColorConstants.Blue
            case ColumnFunction.TimestampMS:    return QColorConstants.Blue
            case ColumnFunction.YValue:         return QColorConstants.DarkGreen
        
