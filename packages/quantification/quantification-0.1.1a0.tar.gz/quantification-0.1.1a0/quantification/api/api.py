from quantification.core import BaseCombinedAPI

from .akshare import AkShareAPI
from .tushare import TuShareAPI
from .spider import SpiderAPI


class DataAPI(BaseCombinedAPI):
    api_classes = [
        TuShareAPI,
        AkShareAPI,
        SpiderAPI
    ]
