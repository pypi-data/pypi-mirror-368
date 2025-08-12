from abc import ABC, abstractmethod
from typing import TypeVar, Generic, TYPE_CHECKING
from datetime import date

from ..env import EnvGetter

if TYPE_CHECKING:
    from .base_asset import BaseAsset
    from ..data import BaseAPI
    from ..trader import BaseOrder, BaseStage, Result, Portfolio

AssetType = TypeVar('AssetType', bound="BaseAsset")


class BaseBroker(Generic[AssetType], ABC, EnvGetter):
    def __init__(self, api: "BaseAPI", start_date: date, end_date: date, stage: type["BaseStage"], **kwargs):
        super().__init__()

        self.api = api
        self.start_date = start_date
        self.end_date = end_date
        self.stage = stage

    @abstractmethod
    def matchable(self, asset: "type[BaseAsset]") -> bool:
        raise NotImplementedError

    @abstractmethod
    def execute_order(self, order: "BaseOrder[AssetType]", portfolio: "Portfolio") -> "Result":
        raise NotImplementedError

    @abstractmethod
    def liquidate_asset(self, asset: "BaseAsset", day: date, stage: "BaseStage") -> int:
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    __str__ = __repr__


__all__ = ['BaseBroker']
