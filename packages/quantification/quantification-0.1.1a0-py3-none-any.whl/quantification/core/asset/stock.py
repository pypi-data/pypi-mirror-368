from abc import ABCMeta, abstractmethod
from typing import overload, Type
from datetime import date
from itertools import chain

import akshare as ak

from .base_asset import BaseAsset

from ..cache import cache_query


class BaseStockExchangeMeta(ABCMeta):
    def __repr__(self: "BaseStockExchange"):
        return self.name()

    __str__ = __repr__


class BaseStockExchange(metaclass=BaseStockExchangeMeta):
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def code(cls) -> str:
        raise NotImplementedError


# 上海证券交易所
class SSE(BaseStockExchange):
    @classmethod
    def name(cls) -> str:
        return "上海证券交易所"

    @classmethod
    def code(cls) -> str:
        return "SH"


# 深圳证券交易所
class SZSE(BaseStockExchange):
    @classmethod
    def name(cls) -> str:
        return "深圳证券交易所"

    @classmethod
    def code(cls) -> str:
        return "SZ"


# 北京证券交易所
class BSE(BaseStockExchange):
    @classmethod
    def name(cls) -> str:
        return "北京证券交易所"

    @classmethod
    def code(cls) -> str:
        return "BJ"


# 香港交易所
class HKEX(BaseStockExchange):
    @classmethod
    def name(cls) -> str:
        return "香港交易所"

    @classmethod
    def code(cls) -> str:
        return "HK"


# 纽约证券交易所
class NYSE(BaseStockExchange):
    @classmethod
    def name(cls) -> str:
        return "纽约证券交易所"

    @classmethod
    def code(cls) -> str:
        return "N"


# 纳斯达克
class NASDAQ(BaseStockExchange):
    @classmethod
    def name(cls) -> str:
        return "纳斯达克"

    @classmethod
    def code(cls) -> str:
        return "O"


# 伦敦证券交易所
class LSE(BaseStockExchange):
    @classmethod
    def name(cls) -> str:
        return "伦敦证券交易所"

    @classmethod
    def code(cls) -> str:
        return "L"


class StockExchange:
    SSE = SSE
    SZSE = SZSE
    BSE = BSE
    HKEX = HKEX
    NYSE = NYSE
    NASDAQ = NASDAQ
    LSE = LSE


def predict_exchange(symbol: str) -> type[BaseStockExchange]:
    if "." not in symbol:
        api = cache_query(update=False)(ak.stock_zh_a_spot)
        code_list = api()["代码"].tolist()
        for code in code_list:
            if code[2:] != symbol: continue

            match code[:2]:
                case "sh":
                    return StockExchange.SSE
                case "sz":
                    return StockExchange.SZSE
                case "bj":
                    return StockExchange.BSE

        raise ValueError(f"无法根据{symbol}判断交易所")

    _, exchange = symbol.split(".")
    match exchange.lower():
        case "sh":
            return StockExchange.SSE
        case "sz":
            return StockExchange.SZSE
        case "bj":
            return StockExchange.BSE
        case _:
            raise ValueError(f"无法根据{symbol}判断交易所")


stock_family: dict[str:type["Stock"]] = {}
SharePosition = dict[date, int]


class Stock(BaseAsset):
    symbol: str = None
    exchange: type[BaseStockExchange] = None

    @classmethod
    def type(cls, *args, **kwargs):
        return "Stock"

    @classmethod
    def class_name(cls, *args, **kwargs):
        return f"股票{cls.symbol}.{cls.exchange.code()}" if cls.symbol else "股票"

    def name(self, *args, **kwargs):
        return f"{self.class_name(*args, **kwargs)}({self.amount}股)"

    @property
    def amount(self, *args, **kwargs):
        return sum(self.share_position.values())

    @property
    def extra(self, *args, **kwargs):
        return {"position": {k.isoformat(): int(v) for k, v in self.share_position.items()}}

    @property
    def is_empty(self):
        return self.amount == 0

    @property
    def copy(self):
        return Stock[self.symbol](self.share_position)

    def available(self, day: date):
        return Stock[self.symbol]({d: s for d, s in self.share_position.items() if d < day})

    def __add__(self, other: "Stock"):
        assert self == other, f"只有同种股票可以相加减, {self.__class__.__name__} != {other.__class__.__name__}"

        return Stock[self.symbol](self.add_shares(other.share_position))

    def __sub__(self, other: "Stock"):
        assert self == other, f"只有同种股票可以相加减, {self.__class__.__name__} != {other.__class__.__name__}"

        day = next(iter(other.share_position.keys()))
        available = self.available(day).amount
        assert available >= other.amount, f"可出售股份不足, {available} < {other.amount}"

        return Stock[self.symbol](self.sub_shares(other.amount))

    def __eq__(self, other):
        return isinstance(other, Stock) and self.symbol == other.symbol

    def __neg__(self):
        return Stock[self.symbol]({k: -v for k, v in self.share_position.items()})

    def __init__(self, share: SharePosition = None):
        assert self.symbol is not None, "未指定股票代码, 无法实例化, 是否应该使用Stock[symbol](...) ?"
        self.share_position = share or {}

    def add_shares(self, share_position: SharePosition) -> SharePosition:
        return {
            k: self.share_position.get(k, 0) + share_position.get(k, 0)
            for k in chain(self.share_position, share_position)
        }

    @overload
    def __class_getitem__(cls, symbol: str):
        ...

    @overload
    def __class_getitem__(cls, symbol_and_exchange: tuple[str, Type[BaseStockExchange]]):
        ...

    def __class_getitem__(cls, arg: str | tuple[str, Type[BaseStockExchange]]):
        if isinstance(arg, str):
            symbol = arg
            exchange = predict_exchange(arg)
        else:
            symbol, exchange = arg

        code = f"{symbol}.{exchange}"
        if not stock_family.get(code):
            stock_family[code] = type(
                f"Stock{symbol}",
                (Stock,),
                {"symbol": symbol, "exchange": exchange},
            )

        return stock_family[code]

    def sub_shares(self, share: int) -> SharePosition:
        remaining_share = share
        new_share_position = {}
        sorted_dates = sorted(self.share_position.keys())
        for sorted_date in sorted_dates:
            current_share = self.share_position[sorted_date]
            if remaining_share <= 0:
                new_share_position[sorted_date] = current_share
                continue
            if current_share <= remaining_share:
                remaining_share -= current_share
            else:
                new_share_position[sorted_date] = current_share - remaining_share
                remaining_share = 0
        return new_share_position


__all__ = ["Stock", "StockExchange"]
