from quantification.core.data import BaseAPI

from .setting import TuShareSetting
from .delegate import *


class TuShareAPI(BaseAPI[TuShareSetting]):
    setting_class = TuShareSetting
    delegate_classes = [
        ProBarDelegate,
        IncomeDelegate,
        CashflowDelegate,
        IndexDailyDelegate,
        DailyBasicDelegate,
        BalanceSheetDelegate,
        FinanceIndicatorDelegate,
    ]
