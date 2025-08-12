from tqdm import tqdm
from functools import lru_cache
from datetime import date, datetime, time

import pandas as pd
import tushare as ts

from quantification.core import (
    Field,
    Stock,
    Config,
    cache_query,
    BaseDelegate,
    StockExchange as E
)

from ..setting import TuShareSetting


class DailyBasicDelegate(BaseDelegate[TuShareSetting]):
    pair = [
        (Field.ST_换手率, "turnover_rate"),
        (Field.ST_自由流通股换手率, "turnover_rate_f"),
        (Field.ST_量比, "volume_ratio"),
        (Field.ST_总市值, "total_mv"),
        (Field.ST_流通市值, "circ_mv"),
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
        df = self.bulk(start_date=start_date, end_date=end_date)

        stock: Stock = kwargs.get("stock")
        exchange = {
            E.SSE: "SH",
            E.SZSE: "SZ",
            E.BSE: "BJ"
        }[stock.exchange]

        data = df[df["ts_code"] == f"{stock.symbol}.{exchange}"]

        data = self.rename_columns(data, "trade_date")
        data = self.use_date_index(data)

        return data

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        index = pd.Series(mask.index)

        for field in fields:
            mask[field] = list(map(lambda x: datetime.combine(x, time(17, 0, 0)), index))

        return mask

    def __init__(self, config: Config, setting: TuShareSetting):
        super().__init__(config, setting)
        self.api = cache_query(update=False)(ts.pro_api(setting.tushare_token).daily_basic)

    @lru_cache()
    def bulk(self, start_date: date, end_date: date):
        rows = []
        for current in tqdm(pd.date_range(start=start_date, end=end_date), "遍历获取daily_basic"):
            rows.append(self.api(
                trade_date=current.strftime("%Y%m%d"),
                adj=self.config.adjust
            ))

        return pd.concat([row for row in rows if not row.empty])
