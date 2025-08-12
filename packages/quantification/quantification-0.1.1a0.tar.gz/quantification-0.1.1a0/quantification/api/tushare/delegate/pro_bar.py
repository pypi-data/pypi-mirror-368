from datetime import date, datetime, time

import pandas as pd
import tushare as ts

from quantification.core import (
    Field,
    Stock,
    cache_query,
    BaseDelegate,
    StockExchange as E
)

from ..setting import TuShareSetting

api = cache_query()(ts.pro_bar)


class ProBarDelegate(BaseDelegate[TuShareSetting]):
    pair = [
        (Field.ST_昨收价, "pre_close"),
        (Field.ST_开盘价, "open"),
        (Field.ST_最高价, "high"),
        (Field.ST_最低价, "low"),
        (Field.ST_收盘价, "close"),
        (Field.ST_涨跌额, "change"),
        (Field.ST_涨跌幅, "pct_chg"),
        (Field.ST_成交量, "vol"),
        (Field.ST_成交额, "amount")
    ]

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

        data = api(
            ts_code=f"{stock.symbol}.{exchange}",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adj=self.config.adjust
        )

        data = self.rename_columns(data, "trade_date")
        data = self.use_date_index(data)

        data[Field.ST_成交额] = data[Field.ST_成交额].apply(lambda x: x / 10)

        return data

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        index = pd.Series(mask.index)

        for field in fields:
            match field:
                case Field.ST_昨收价:
                    mask[field] = list(map(lambda x: datetime.combine(x, time(0, 0, 0)), index))
                case Field.ST_开盘价:
                    mask[field] = list(map(lambda x: datetime.combine(x, time(9, 30, 0)), index))
                case Field.ST_最高价 | Field.ST_最低价 | Field.ST_收盘价 | Field.ST_涨跌额 | Field.ST_涨跌幅 | Field.ST_成交量 | Field.ST_成交额:
                    mask[field] = list(map(lambda x: datetime.combine(x, time(17, 0, 0)), index))

        return mask
