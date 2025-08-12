from datetime import date, datetime, timedelta, time

import pandas as pd
import akshare as ak

from quantification.core import (
    Field,
    cache_query,
    BaseDelegate
)

from ..setting import AkShareSetting

api = cache_query()(ak.macro_china_lpr)


class MacroChinaLPR(BaseDelegate[AkShareSetting]):
    pair = [
        (Field.RATE_LPR1年, "LPR1Y"),
        (Field.RATE_LPR5年, "LPR5Y"),
        (Field.RATE_短期贷款, "RATE_2"),
        (Field.RATE_中长期贷款, "RATE_1"),
    ]

    def has_field(self, field: Field, **kwargs):
        return self.field2str.get(field) is not None

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        df = api()

        df = self.rename_columns(df, "TRADE_DATE")
        df = self.use_date_index(df)

        return df

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        index = pd.Series(mask.index)

        for field in fields:
            mask[field] = list(map(lambda x: datetime.combine(x + timedelta(days=1), time(0, 0, 0)), index))

        return mask
