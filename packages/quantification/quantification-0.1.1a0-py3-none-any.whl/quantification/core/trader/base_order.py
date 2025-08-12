from typing import TypeVar, Generic, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from ..asset import BaseAsset

AssetType = TypeVar('AssetType', bound="BaseAsset")


class BaseOrder(Generic[AssetType], ABC):
    def __init__(self, asset: type[AssetType], category: str, *args, **kwargs):
        self.asset = asset
        self.category = category

    def type(self):
        return self.__class__.__name__

    @property
    @abstractmethod
    def extra(self):
        raise NotImplementedError

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError

    __str__ = __repr__


OrderType = TypeVar('OrderType', bound=BaseOrder)


class Result(Generic[OrderType]):
    def __init__(self, *, order: OrderType, sold: list["BaseAsset"], brought: list["BaseAsset"]):
        self.order = order
        self.sold = sold
        self.brought = brought

    def __repr__(self):
        return f"<Result sold={self.sold} brought={self.brought}>"

    __str__ = __repr__


__all__ = ['BaseOrder', 'Result']
