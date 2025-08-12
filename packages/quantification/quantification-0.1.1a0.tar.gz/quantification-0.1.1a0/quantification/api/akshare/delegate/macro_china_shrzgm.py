from datetime import date, datetime, time

import pandas as pd
import akshare as ak

from quantification.core import (
    Field,
    cache_query,
    BaseDelegate
)

from ..setting import AkShareSetting

api = cache_query()(ak.macro_china_shrzgm)


class MacroChinaSHRZGM(BaseDelegate[AkShareSetting]):
    pair = [
        (Field.AFRE_总增量, "社会融资规模增量"),
        (Field.AFRE_人民币贷款增量, "其中-人民币贷款"),
        (Field.AFRE_委托贷款外币贷款增量, "其中-委托贷款外币贷款"),
        (Field.AFRE_委托贷款增量, "其中-委托贷款"),
        (Field.AFRE_信托贷款增量, "其中-信托贷款"),
        (Field.AFRE_未贴现银行承兑汇票增量, "其中-未贴现银行承兑汇票"),
        (Field.AFRE_企业债券增量, "其中-企业债券"),
        (Field.AFRE_非金融企业境内股票融资增量, "其中-非金融企业境内股票融资"),
    ]

    def has_field(self, field: Field, **kwargs):
        return self.field2str.get(field) is not None

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        df = api()

        df = self.rename_columns(df, "月份")
        df = self.use_date_index(df, lambda x: datetime.strptime(x, "%Y%m").date())

        return df

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        index = pd.Series(mask.index)

        for field in fields:
            mask[field] = list(map(lambda x: datetime.combine(x + pd.DateOffset(months=1), time(0, 0, 0)), index))

        return mask
