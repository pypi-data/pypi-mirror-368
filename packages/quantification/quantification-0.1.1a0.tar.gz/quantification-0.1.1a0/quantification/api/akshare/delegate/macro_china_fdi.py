from datetime import date, datetime, time

import pandas as pd
import akshare as ak

from quantification.core import (
    Field,
    cache_query,
    BaseDelegate
)

from ..setting import AkShareSetting

api = cache_query()(ak.macro_china_fdi)


class MacroChinaFDI(BaseDelegate[AkShareSetting]):
    pair = [
        (Field.FDI_当月, "当月"),
        (Field.FDI_当月同比增长, "当月-同比增长"),
        (Field.FDI_当月环比增长, "当月-环比增长"),
        (Field.FDI_累计, "累计"),
        (Field.FDI_累计同比增长, "累计-同比增长")
    ]

    def has_field(self, field: Field, **kwargs):
        return self.field2str.get(field) is not None

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        df = api()
        df = self.rename_columns(df, "月份")
        df = self.use_date_index(df, lambda x: datetime.strptime(x, "%Y年%m月份").date())

        df[Field.FDI_当月] = df[Field.FDI_当月].apply(lambda x: x / 1e4)
        df[Field.FDI_累计] = df[Field.FDI_累计].apply(lambda x: x / 1e4)

        return df

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        index = pd.Series(mask.index)

        for field in fields:
            mask[field] = list(map(lambda x: datetime.combine(x +  pd.DateOffset(months=1), time(0, 0, 0)), index))

        return mask
