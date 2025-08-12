from abc import ABC
from datetime import date, datetime, timedelta

import pandas as pd

from quantification.core import (
    Stock,
    Field,
    Config,
    BaseDelegate,
    StockExchange as E
)

from ..setting import TuShareSetting


class TushareSheetDelegate(BaseDelegate[TuShareSetting], ABC):
    def has_field(self, field: Field, **kwargs):
        if self.field2str.get(field) is None:
            return False

        stock = kwargs.get("stock")
        assert stock is not None, "请传入stock参数, 如stock=Stock['000001']"
        assert issubclass(stock, Stock), f"stock参数必须为Stock子类, 实际为{type(stock)}"

        if stock.exchange not in [E.SZSE, E.BSE, E.SSE]:
            return False

        return True

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        stock: Stock = kwargs.get("stock")
        exchange = {
            E.SSE: "SH",
            E.SZSE: "SZ",
            E.BSE: "BJ"
        }[stock.exchange]

        data = self.api(
            ts_code=f"{stock.symbol}.{exchange}",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            fields=",".join([*self.field2str.values(), "ann_date", "end_date", "update_flag"]),
        )

        data = data[data['update_flag'] == '1']
        data = self.rename_columns(data, "end_date")
        data = self.use_date_index(data)

        return data

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        datetime_column = data["ann_date"].apply(
            lambda x: (datetime.strptime(x, "%Y%m%d") + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        )
        for field in fields:
            mask[field] = datetime_column

        return mask

    def __init__(self, config: Config, setting: TuShareSetting):
        super().__init__(config, setting)
        self.api = None
