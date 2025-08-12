from datetime import date, datetime, time

import pandas as pd
import akshare as ak

from quantification.core import (
    Field,
    cache_query,
    BaseDelegate
)

from ..setting import AkShareSetting

api = cache_query()(ak.macro_china_qyspjg)


class MacroChinaQYSPJG(BaseDelegate[AkShareSetting]):
    pair = [
        (Field.CGPI_总指数, "总指数-指数值"),
        (Field.CGPI_总指数同比增长, "总指数-同比增长"),
        (Field.CGPI_总指数环比增长, "总指数-环比增长"),
        (Field.CGPI_农产品, "农产品-指数值"),
        (Field.CGPI_农产品同比增长, "农产品-同比增长"),
        (Field.CGPI_农产品环比增长, "农产品-环比增长"),
        (Field.CGPI_矿产品, "矿产品-指数值"),
        (Field.CGPI_矿产品同比增长, "矿产品-同比增长"),
        (Field.CGPI_矿产品环比增长, "矿产品-环比增长"),
        (Field.CGPI_煤油电, "煤油电-指数值"),
        (Field.CGPI_煤油电同比增长, "煤油电-同比增长"),
        (Field.CGPI_煤油电环比增长, "煤油电-环比增长"),
    ]

    def has_field(self, field: Field, **kwargs):
        return self.field2str.get(field) is not None

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        df = api()

        df = self.rename_columns(df, "月份")
        df = self.use_date_index(df, lambda x: datetime.strptime(x, "%Y年%m月份").date())

        return df

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        index = pd.Series(mask.index)

        for field in fields:
            mask[field] = list(map(lambda x: datetime.combine(x + pd.DateOffset(months=1), time(0, 0, 0)), index))

        return mask
