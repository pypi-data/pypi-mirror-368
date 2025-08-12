from datetime import datetime

import pandas as pd

from .field import Field


class DataPanel(pd.DataFrame):
    def __init__(self, data: pd.DataFrame = None, mask: pd.DataFrame = None):
        data = data if data is not None else pd.DataFrame()
        mask = mask if mask is not None else pd.DataFrame()
        self.mask = mask
        super().__init__(data)

        if self.shape[0] != 0:
            assert type(self.index) == pd.DatetimeIndex, \
                f"DataPanel data的索引必须为pd.DatetimeIndex, 实际为{type(self.index)}"

        for col in self.columns:
            assert type(col) == Field, \
                f"DataPanel data的列必须为core.Field, {col}实际为{type(col)}"

        if self.mask.shape[0] != 0:
            assert type(self.index) == pd.DatetimeIndex, \
                f"DataPanel mask的索引必须为pd.DatetimeIndex, 实际为{type(self.index)}"

        for col in self.columns:
            assert type(col) == Field, \
                f"DataPanel mask的列必须为core.Field, {col}实际为{type(col)}"

        assert self.columns.equals(self.mask.columns) and self.shape == self.mask.shape, \
            f"DataPanel data与mask的结构不一致, data:\n{self}\nmask:\n{self.mask} "

    def __lshift__(self, other: "DataPanel"):
        assert isinstance(other, DataPanel), f"DataPanel只能与DataPanel进行lshift操作, 实际为{type(other)}"
        return DataPanel(self.join(other, how='outer'), self.mask.join(other.mask, how='outer'))

    def on(self, d: datetime) -> pd.DataFrame:
        return self.where((self.mask <= d) | self.isna(), other="invalid")[:d.date()]


__all__ = ["DataPanel"]
