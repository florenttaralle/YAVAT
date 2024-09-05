from datetime import timedelta
import re
import pandas as pd, numpy as np

class TimedeltaParser:
    DT_RE = re.compile("(?:(\d+):)?(?:(\d+):)?(\d+(?:\.\d*)?)")

    @classmethod
    def from_str(cls, x: str) -> timedelta | None:
        if not isinstance(x, str): return None
        match = cls.DT_RE.match(x)
        if not match: return None
        td = timedelta(
            hours           = int(match[1] or 0),
            minutes         = int(match[2] or 0),
            seconds         = float(match[3]),
        )
        return td

    @classmethod
    def convert_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """ convert in-place any object (str) column to np.timedelta64 if compatible """
        for column in df.columns:
            if df.dtypes[column] == object: # object -> str
                timedeltas = df[column].apply(cls.from_str)
                if np.issubdtype(timedeltas.dtype, np.timedelta64):
                    df[column] = timedeltas
        return df
    