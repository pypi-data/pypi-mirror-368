from datetime import date, datetime, time

import pandas as pd
import tushare as ts

from quantification.core import (
    Field,
    Config,
    cache_query,
    BaseDelegate,
)

from ..setting import TuShareSetting


class IndexDailyDelegate(BaseDelegate[TuShareSetting]):
    pair = [
        (Field.IN_开盘点位, "open"),
        (Field.IN_收盘点位, "close"),
        (Field.IN_最高点位, "high"),
        (Field.IN_最低点位, "low")
    ]

    def has_field(self, field: Field, **kwargs):
        if self.field2str.get(field) is None:
            return False

        index = kwargs.get("index")
        assert index is not None, "请传入index='xxx'"
        assert type(index) == str, f"index必须为字符串, 实际为{type(index)}"

        return True

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        data = self.api(
            ts_code=kwargs.get("index"),
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )

        data = self.rename_columns(data, "trade_date")
        data = self.use_date_index(data)

        return data

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        index = pd.Series(mask.index)

        for field in fields:
            match field:
                case Field.IN_开盘点位:
                    mask[field] = list(map(lambda x: datetime.combine(x, time(9, 30, 0)), index))
                case Field.IN_收盘点位 | Field.IN_最高点位 | Field.IN_最低点位:
                    mask[field] = list(map(lambda x: datetime.combine(x, time(17, 0, 0)), index))

        return mask

    def __init__(self, config: Config, setting: TuShareSetting):
        super().__init__(config, setting)
        self.api = cache_query()(ts.pro_api(setting.tushare_token).index_daily)
