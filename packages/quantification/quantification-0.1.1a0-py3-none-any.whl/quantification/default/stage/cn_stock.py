from enum import auto
from datetime import time

from quantification import BaseStage


class StockStageCN(BaseStage):
    盘前 = auto()
    开盘 = auto()
    收盘 = auto()
    盘后 = auto()

    @property
    def time(self) -> time:
        return {
            StockStageCN.盘前: time(0, 0),
            StockStageCN.开盘: time(9, 30),
            StockStageCN.收盘: time(15, 0),
            StockStageCN.盘后: time(23, 59),
        }[self]


__all__ = ['StockStageCN']
