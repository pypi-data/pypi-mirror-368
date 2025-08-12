import tushare as ts

from quantification.core import (
    Field,
    Config,
    cache_query
)

from .common import TushareSheetDelegate
from ..setting import TuShareSetting


class BalanceSheetDelegate(TushareSheetDelegate):
    pair = [
        (Field.BS_总股本, "total_share"),
        (Field.BS_库存股, "treasury_share"),
        (Field.BS_资本公积, "cap_rese"),
        (Field.BS_盈余公积, "surplus_rese"),
        (Field.BS_未分配利润, "undistr_porfit"),
        (Field.BS_股东权益合计, "total_hldr_eqy_inc_min_int"),
        (Field.BS_归母股东权益合计, "total_hldr_eqy_exc_min_int"),
        (Field.BS_货币资金, "money_cap"),
        (Field.BS_交易性金融资产, "trad_asset"),
        (Field.BS_应收票据, "notes_receiv"),
        (Field.BS_应收账款, "accounts_receiv"),
        (Field.BS_应收股利, "div_receiv"),
        (Field.BS_应收利息, "int_receiv"),
        (Field.BS_其他应收款, "oth_receiv"),
        (Field.BS_预付款项, "prepayment"),
        (Field.BS_存货, "inventories"),
        (Field.BS_一年内到期的非流动资产, "nca_within_1y"),
        (Field.BS_可供出售金融资产, "fa_avail_for_sale"),
        (Field.BS_持有至到期投资, "htm_invest"),
        (Field.BS_长期股权投资, "lt_eqt_invest"),
        (Field.BS_投资性房地产, "invest_real_estate"),
        (Field.BS_定期存款, "time_deposits"),
        (Field.BS_长期应收款, "lt_rec"),
        (Field.BS_固定资产, "fix_assets"),
        (Field.BS_在建工程, "cip"),
        (Field.BS_无形资产, "intan_assets"),
        (Field.BS_研发支出, "r_and_d"),
        (Field.BS_商誉, "goodwill"),
        (Field.BS_流动资产合计, "total_cur_assets"),
        (Field.BS_非流动资产合计, "total_nca"),
        (Field.BS_资产合计, "total_assets"),
        (Field.BS_短期借款, "st_borr"),
        (Field.BS_长期借款, "lt_borr"),
        (Field.BS_交易性金融负债, "trading_fl"),
        (Field.BS_应付票据, "notes_payable"),
        (Field.BS_应付账款, "acct_payable"),
        (Field.BS_应付职工薪酬, "payroll_payable"),
        (Field.BS_应付利息, "int_payable"),
        (Field.BS_应付股利, "div_payable"),
        (Field.BS_应付短期债券, "st_bonds_payable"),
        (Field.BS_应付债券, "bond_payable"),
        (Field.BS_长期应付款, "lt_payable"),
        (Field.BS_预收款项, "adv_receipts"),
        (Field.BS_一年内到期的非流动负债, "non_cur_liab_due_1y"),
        (Field.BS_流动负债合计, "total_cur_liab"),
        (Field.BS_非流动负债合计, "total_ncl"),
        (Field.BS_负债合计, "total_liab"),
    ]

    def __init__(self, config: Config, setting: TuShareSetting):
        super().__init__(config, setting)
        self.api = cache_query()(ts.pro_api(setting.tushare_token).balancesheet)
