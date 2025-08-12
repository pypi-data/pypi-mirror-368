import inspect
from typing import TYPE_CHECKING, Literal, overload

from .base_order import BaseOrder

if TYPE_CHECKING:
    from ..asset import Stock


class StockOrder(BaseOrder["Stock"]):
    @overload
    def __init__(self, asset: "type[Stock]|Stock", category: Literal["buy"] | Literal["sell"]):
        ...

    @overload
    def __init__(self, asset: "type[Stock]|Stock", category: Literal["buy"] | Literal["sell"], share: int):
        ...

    @overload
    def __init__(self, asset: "type[Stock]|Stock", category: Literal["buy"] | Literal["sell"], value: float):
        ...

    def __init__(
            self,
            asset: "type[Stock]|Stock",
            category: Literal["buy"] | Literal["sell"],
            *,
            share: int = None,
            value: float = None
    ):
        super().__init__(asset if inspect.isclass(asset) else asset.__class__, category)
        self.share = share
        self.value = value

    @property
    def extra(self):
        if self.share:
            return {"share": self.share, }

        if self.value:
            return {"value": self.value, }

        return {}

    def __repr__(self):
        return f"<股票交易指令 {self.category} {self.asset}>"

    __str__ = __repr__


__all__ = ["StockOrder"]
