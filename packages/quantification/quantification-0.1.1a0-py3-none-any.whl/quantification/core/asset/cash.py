from .base_asset import BaseAsset

cash_family: dict[str:type["Cash"]] = {}


class Cash(BaseAsset):
    symbol: str = None
    is_closeable = False

    @classmethod
    def type(cls, *args, **kwargs):
        return "Cash"

    @classmethod
    def class_name(cls, *args, **kwargs):
        return f"现金{cls.symbol}" if cls.symbol else "全部现金"

    def name(self, *args, **kwargs):
        return f"{self.class_name()}({self.amount}元)"

    @property
    def amount(self, *args, **kwargs):
        return self.value

    @property
    def extra(self, *args, **kwargs):
        return {}

    @property
    def is_empty(self):
        return self.value == 0

    @property
    def copy(self):
        return Cash[self.symbol](self.value)

    def available(self, *args, **kwargs):
        return Cash[self.symbol](self.value)

    def __add__(self, other: "Cash"):
        assert self == other, f"只能和Cash相加, 实际类型{type(other)}"

        return Cash[self.symbol](self.value + other.value)

    def __sub__(self, other: "Cash"):
        assert self == other, f"只能和Cash相减, 实际类型{type(other)}"

        return Cash[self.symbol](self.value - other.value)

    def __eq__(self, other: "Cash"):
        return isinstance(other, Cash) and self.symbol == other.symbol

    def __neg__(self):
        return Cash[self.symbol](-self.value)

    def __init__(self, value: float = 0):
        assert self.symbol is not None, "未指定现金类型, 无法实例化"
        self.value = value

    def __class_getitem__(cls, symbol: str):
        if not cash_family.get(symbol):
            cash_family[symbol] = type(
                f"Cash{symbol}",
                (Cash,),
                {"symbol": symbol},
            )

        return cash_family[symbol]


RMB = Cash["RMB"]
HKD = Cash["HKD"]
USD = Cash["USD"]

__all__ = ["Cash", "RMB", "HKD", "USD"]
