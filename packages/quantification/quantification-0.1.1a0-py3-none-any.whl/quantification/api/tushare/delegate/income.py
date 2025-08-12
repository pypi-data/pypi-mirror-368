import tushare as ts

from quantification.core import (
    Field,
    Config,
    cache_query
)

from .common import TushareSheetDelegate
from ..setting import TuShareSetting


class IncomeDelegate(TushareSheetDelegate):
    pair = [
        (Field.IS_营业总收入, "total_revenue"),
        (Field.IS_营业总成本, "total_cogs"),
        (Field.IS_营业利润, "operate_profit"),
        (Field.IS_利润总额, "total_profit"),
        (Field.IS_息税前利润, "ebit"),
        (Field.IS_息税折旧摊销前利润, "ebitda"),
        (Field.IS_所得税费用, "income_tax"),
        (Field.IS_净利润, "n_income"),
        (Field.IS_归母净利润, "n_income_attr_p"),
        (Field.IS_综合收益, "t_compr_income"),
        (Field.IS_归母综合收益, "compr_inc_attr_p"),
        (Field.IS_销售费用, "sell_exp"),
        (Field.IS_管理费用, "admin_exp"),
        (Field.IS_财务费用, "fin_exp"),
        (Field.IS_研发费用, "rd_exp"),
    ]

    def __init__(self, config: Config, setting: TuShareSetting):
        super().__init__(config, setting)
        self.api = cache_query()(ts.pro_api(setting.tushare_token).income)
