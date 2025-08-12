from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable
from datetime import date

import pandas as pd
from pydantic import BaseModel

from .field import Field
from .panel import DataPanel

from ..configure import Config

SettingType = TypeVar('SettingType', bound=BaseModel)


class BaseDelegate(ABC, Generic[SettingType]):
    pair: list[tuple[Field, str]]
    field2str: dict[Field, str]
    str2field: dict[str, Field]

    DATE_FIELD = "日期"

    def __init_subclass__(cls, **kwargs):
        if ABC in cls.__bases__: return

        assert hasattr(cls, 'pair'), f'{cls.__name__}必须实现类属性pair'

        cls.field2str = {k: v for k, v in cls.pair}
        cls.str2field = {v: k for k, v in cls.pair}

    def __init__(self, config: Config, setting: SettingType) -> None:
        self.config = config
        self.setting = setting

    def rename_columns(self, data: pd.DataFrame, date_field: str) -> pd.DataFrame:
        data = data.rename(columns=self.str2field)
        data = data.rename(columns={date_field: self.DATE_FIELD})

        return data

    def use_date_index(self, data: pd.DataFrame, formatter: Callable = None) -> pd.DataFrame:
        if formatter:
            data[self.DATE_FIELD] = data[self.DATE_FIELD].apply(formatter)

        data[self.DATE_FIELD] = pd.to_datetime(data[self.DATE_FIELD])
        data = data.set_index(self.DATE_FIELD)
        data = data.sort_index()

        return data

    def execute(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> DataPanel:
        data = self.query(start_date, end_date, fields, **kwargs)
        mask = self.mask(data, start_date, end_date, fields, **kwargs)
        data = data[fields]
        mask = mask[fields]
        data = data[start_date:end_date]
        mask = mask[start_date:end_date]
        return DataPanel(data, mask)

    @abstractmethod
    def has_field(self, field: Field, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        raise NotImplementedError


__all__ = ["BaseDelegate"]
