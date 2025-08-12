import tushare as ts

from quantification.core import (
    Field,
    Config,
    cache_query
)

from .common import TushareSheetDelegate
from ..setting import TuShareSetting


class FinanceIndicatorDelegate(TushareSheetDelegate):
    pair = [
        (Field.FI_基本每股收益, "eps"),
        (Field.FI_稀释每股收益, "dt_eps"),
        (Field.FI_期末摊薄每股收益, "diluted2_eps"),
        (Field.FI_每股营业总收入, "total_revenue_ps"),
        (Field.FI_每股营业收入, "revenue_ps"),
        (Field.FI_每股资本公积, "capital_rese_ps"),
        (Field.FI_每股盈余公积, "surplus_rese_ps"),
        (Field.FI_每股未分配利润, "undist_profit_ps"),
        (Field.FI_每股净资产, "bps"),
        (Field.FI_每股经营活动产生的现金流量净额, "ocfps"),
        (Field.FI_每股留存收益, "retainedps"),
        (Field.FI_每股现金流量净额, "cfps"),
        (Field.FI_每股息税前利润, "ebit_ps"),
        (Field.FI_每股企业自由现金流量, "fcff_ps"),
        (Field.FI_每股股东自由现金流量, "fcfe_ps"),
        (Field.FI_流动比率, "current_ratio"),
        (Field.FI_速动比率, "quick_ratio"),
        (Field.FI_现金比率, "cash_ratio"),
        (Field.FI_利息保障倍数, "ebit_to_interest"),
        (Field.FI_存货周转率, "inv_turn"),
        (Field.FI_应收账款周转率, "ar_turn"),
        (Field.FI_流动资产周转率, "ca_turn"),
        (Field.FI_固定资产周转率, "fa_turn"),
        (Field.FI_总资产周转率, "assets_turn"),
        (Field.FI_营业周期, "turn_days"),
        (Field.FI_企业自由现金流量, "fcff"),
        (Field.FI_股权自由现金流量, "fcfe"),
        (Field.FI_销售净利率, "netprofit_margin"),
        (Field.FI_销售毛利率, "grossprofit_margin"),
        (Field.FI_销售成本率, "cogs_of_sales"),
        (Field.FI_销售期间费用率, "expense_of_sales"),
        (Field.FI_净资产收益率, "roe"),
        (Field.FI_加权平均净资产收益率, "roe_waa"),
        (Field.FI_扣除非经常损益净资产收益率, "roe_dt"),
        (Field.FI_总资产报酬率, "roa"),
        (Field.FI_总资产净利润, "npta"),
        (Field.FI_投入资本回报率, "roic"),
        (Field.FI_平均净资产收益率, "roe_avg"),
        (Field.FI_资产负债率, "debt_to_assets"),
        (Field.FI_权益乘数, "assets_to_eqt"),
        (Field.FI_产权比率, "debt_to_eqt"),
    ]

    def __init__(self, config: Config, setting: TuShareSetting):
        super().__init__(config, setting)
        self.api = cache_query()(ts.pro_api(setting.tushare_token).fina_indicator)
