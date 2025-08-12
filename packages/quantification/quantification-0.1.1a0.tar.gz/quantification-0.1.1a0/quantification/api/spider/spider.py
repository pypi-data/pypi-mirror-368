from quantification.core.data import BaseAPI

from .setting import SpiderSetting
from .delegate import *


class SpiderAPI(BaseAPI[SpiderSetting]):
    setting_class = SpiderSetting
    delegate_classes = [
        BaiduIndexDelegate
    ]
