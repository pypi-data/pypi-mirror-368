from abc import ABCMeta, abstractmethod

from ..env import EnvGetter


class BaseAssetMeta(ABCMeta):
    def __repr__(self: "BaseAsset"):
        return self.class_name()

    __str__ = __repr__


class BaseAsset(EnvGetter, metaclass=BaseAssetMeta):
    is_closeable = True  # 若为True, 当empty时将从Portfolio中移除该资产

    @classmethod
    @abstractmethod
    def type(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def class_name(cls, *args, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def name(self, *args, **kwargs) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def amount(self, *args, **kwargs) -> int:
        """
        资产数额
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def extra(self, *args, **kwargs) -> dict:
        """
        资产额外信息
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        """
        若为True, 则会在Portfolio中移除该资产
        """
        raise NotImplementedError

    @abstractmethod
    def available(self, *args, **kwargs):
        """
        获取该资产可用于出售的部分
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def copy(self, *args, **kwargs):
        """
        复制资产对象
        """
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other: "BaseAsset"):
        """
        购买同一种资产
        :param other: 同一种资产
        """
        raise NotImplementedError

    @abstractmethod
    def __sub__(self, other: "BaseAsset"):
        """
        出售该资产的一部分
        :param other: 同一种资产
        """
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other: "BaseAsset"):
        """
        判断是否为同一种资产
        :param other: 任意资产
        """
        raise NotImplementedError


    @abstractmethod
    def __neg__(self):
        """
        转化为空头头寸
        """
        raise NotImplementedError

    def __repr__(self):
        return self.name()

    __str__ = __repr__


__all__ = ["BaseAsset"]
