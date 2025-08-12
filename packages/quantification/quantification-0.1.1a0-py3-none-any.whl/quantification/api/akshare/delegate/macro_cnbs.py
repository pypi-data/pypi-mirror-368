from datetime import date, datetime, time

import pandas as pd
import akshare as ak

from quantification.core import (
    Field,
    cache_query,
    BaseDelegate
)

from ..setting import AkShareSetting

api = cache_query()(ak.macro_cnbs)


class MacroCNBS(BaseDelegate[AkShareSetting]):
    pair = [
        (Field.LEV_居民部门, "居民部门"),
        (Field.LEV_非金融企业部门, "非金融企业部门"),
        (Field.LEV_政府部门, "政府部门"),
        (Field.LEV_中央政府, "中央政府"),
        (Field.LEV_地方政府, "地方政府"),
        (Field.LEV_实体经济部门, "实体经济部门"),
        (Field.LEV_金融部门资产方, "金融部门资产方"),
        (Field.LEV_金融部门负债方, "金融部门负债方")
    ]

    def has_field(self, field: Field, **kwargs):
        return self.field2str.get(field) is not None

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        df = api()

        df = self.rename_columns(df, "年份")
        df = self.use_date_index(df)

        return df

    def mask(self, data: pd.DataFrame, start_date: date, end_date: date, fields: list[Field], **kwargs) -> pd.DataFrame:
        mask = pd.DataFrame(index=data.index, columns=data.columns)
        index = pd.Series(mask.index)

        for field in fields:
            mask[field] = list(map(lambda x: datetime.combine(x + pd.DateOffset(months=1), time(0, 0, 0)), index))

        return mask
