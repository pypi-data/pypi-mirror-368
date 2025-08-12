import tushare as ts

from quantification.core import (
    Field,
    Config,
    cache_query
)

from .common import TushareSheetDelegate
from ..setting import TuShareSetting


class CashflowDelegate(TushareSheetDelegate):
    pair = [
        (Field.CS_经营活动现金流入, "c_inf_fr_operate_a"),
        (Field.CS_经营活动现金流出, "st_cash_out_act"),
        (Field.CS_经营活动净现金流, "n_cashflow_act"),
        (Field.CS_投资活动现金流入, "stot_inflows_inv_act"),
        (Field.CS_投资活动现金流出, "stot_out_inv_act"),
        (Field.CS_投资活动净现金流, "n_cashflow_inv_act"),
        (Field.CS_筹资活动现金流入, "stot_cash_in_fnc_act"),
        (Field.CS_筹资活动现金流出, "stot_cashout_fnc_act"),
        (Field.CS_筹资活动净现金流, "n_cash_flows_fnc_act"),
        (Field.CS_现金及现金等价物净增加额, "n_incr_cash_cash_equ"),
    ]

    def __init__(self, config: Config, setting: TuShareSetting):
        super().__init__(config, setting)
        self.api = cache_query()(ts.pro_api(setting.tushare_token).cashflow)
