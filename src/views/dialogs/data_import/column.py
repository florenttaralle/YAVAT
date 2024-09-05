import attr
from typing import List
import numpy as np
from pandas import Series
from .parse_timedelta import TimedeltaParser
from .column_function import ColumnFunction


@attr.define
class Column:
    id:         int
    series:     Series
    name:       str
    example:    str|None
    min:        object
    max:        object
    nb_values:  int
    cfunction:  ColumnFunction          = attr.field(init=False)
    cfunctions: List[ColumnFunction]    = attr.field(init=False)

    def __repr__(self) -> str:
        return f"<{self.id}|{self.name}|{self.series.dtype.name} on [{self.min};{self.max}]>"

    @property
    def dtype(self):
        return self.series.dtype

    def __attrs_post_init__(self):
        self.cfunctions     = ColumnFunction.applicable_functions(self.dtype, self.nb_values)
        self.cfunction      = ColumnFunction.Ignored if len(self.cfunctions) else ColumnFunction.NotApplicable

    @property
    def usable(self) -> bool:
        return len(self.cfunctions) > 0

    @property
    def used(self) -> bool:
        return self.cfunction.used
    
    def from_str(self, value):
        if np.issubdtype(self.series.dtype, np.timedelta64):
            value = TimedeltaParser().from_str(value)
            assert value is not None
            return value
        elif np.issubdtype(self.series.dtype, np.integer):                
            return int(value)
        else:
            return float(value)
    
    def set_min(self, value) -> bool:
        try:
            self.min = self.from_str(value)
        except:
            return False
        return True
    
    def set_max(self, value) -> bool:
        try:
            self.max = self.from_str(value)
        except:
            return False
        return True
    