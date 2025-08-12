from datetime import date, datetime, time

import pandas as pd
import akshare as ak

from quantification.core import (
    Field,
    Stock,
    cache_query,
    BaseDelegate,
    StockExchange as E
)

from ..setting import AkShareSetting

api = cache_query()(ak.stock_zh_a_hist)


class StockZHAHist(BaseDelegate[AkShareSetting]):
    pair = [
        (Field.ST_开盘价, "开盘"),
        (Field.ST_最高价, "最高"),
        (Field.ST_最低价, "最低"),
        (Field.ST_收盘价, "收盘"),
        (Field.ST_涨跌额, "涨跌额"),
        (Field.ST_涨跌幅, "涨跌幅"),
        (Field.ST_成交量, "成交量"),
        (Field.ST_成交额, "成交额"),
        (Field.ST_振幅, "振幅"),
        (Field.ST_换手率, "换手率")
    ]

    def has_field(self, field: Field, **kwargs):
        if not self.field2str.get(field) is not None:
            return False

        stock = kwargs.get("stock")
        assert stock is not None, "请传入stock参数, 如stock=Stock['000001']"
        assert issubclass(stock, Stock), f"stock参数必须为Stock子类, 实际为{type(stock)}"

        if stock.exchange not in [E.SZSE, E.BSE, E.SSE]:
            return False

        return True

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        stock: Stock = kwargs.get("stock")
        df = api(
            symbol=stock.symbol,
            period="daily",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust=self.config.adjust
        )

        df = self.rename_columns(df, "日期")
        df = self.use_date_index(df)

        df[Field.ST_成交额] = df[Field.ST_成交额].apply(lambda x: x / 1e4)
        df[Field.ST_涨跌额] = df[Field.ST_涨跌额].apply(lambda x: x / 1e4)

        return df

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
