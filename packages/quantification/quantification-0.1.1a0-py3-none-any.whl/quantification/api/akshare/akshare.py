from quantification.core.data import BaseAPI

from .setting import AkShareSetting

from .delegate import *


class AkShareAPI(BaseAPI[AkShareSetting]):
    setting_class = AkShareSetting
    delegate_classes = [
        MacroCNBS,
        StockZHAHist,
        MacroChinaFDI,
        MacroChinaLPR,
        MacroChinaSHRZGM,
        MacroChinaQYSPJG,
    ]
