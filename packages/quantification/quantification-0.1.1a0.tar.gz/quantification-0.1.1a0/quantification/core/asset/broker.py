from typing import TYPE_CHECKING
from datetime import timedelta, date, time

from pandas import to_datetime

from .cash import RMB
from .stock import Stock
from .stock import StockExchange as E
from .base_broker import BaseBroker

from ..logger import logger
from ..data.field import Field
from ..data.base_api import BaseAPI
from ..trader.order import StockOrder
from ..trader.base_order import Result
from ..trader.base_stage import BaseStage

if TYPE_CHECKING:
    from .base_asset import BaseAsset
    from ..trader import Portfolio


class StockBrokerCN(BaseBroker[Stock]):
    def matchable(self, asset: "type[BaseAsset]") -> bool:
        if not issubclass(asset, Stock):
            logger.trace(f"{asset}不是股票, {self}无法处理, 交给下一个Broker")
            return False

        if not asset.exchange in [E.SSE, E.SZSE, E.BSE]:
            logger.trace(f"{asset}不属于上交所|深交所|北交所, {self}无法处理, 交给下一个Broker")
            return False

        return True

    def execute_order(self, order: StockOrder, portfolio: "Portfolio") -> Result | None:
        assert self.env is not None, "无法获取env"

        match self.env.time:
            case time(hour=9, minute=30, second=0):
                field = Field.ST_开盘价
            case time(hour=15, minute=0, second=0):
                field = Field.ST_收盘价
            case _:
                raise ValueError("StockBrokerCN只支持在9:30和15:00撮合交易")

        df = self.api.query(
            self.start_date,
            self.end_date,
            [Field.ST_开盘价, Field.ST_收盘价],
            stock=Stock[order.asset.symbol]
        )

        try:
            price = df.at[to_datetime(self.env.date), field]
        except KeyError:
            logger.warning(f"{order.asset}在 {self.env.date} {self.env.time} 无价格信息")
            return None

        logger.trace(f"{self}撮合交易{order}: 日期{self.env.date} 时间{self.env.time} 价格{price}")

        match order.category:
            case "buy":
                available_rmb = portfolio[RMB][0].amount

                if order.share:
                    share = order.share
                elif order.value:
                    share = int(order.value / price)
                else:
                    share = available_rmb / price

                if self.round_lot:
                    share = share // 100 * 100

                if share == 0:
                    logger.warning(f"购买股数为0, 跳过买入指令")
                    return None

                value = price * share

                if not self.allow_debt and value > available_rmb:
                    logger.warning(f"可用RMB不足以购买{share}股({available_rmb}<{value}), 跳过买入指令")
                    return None

                return Result(
                    order=order,
                    sold=[RMB(value)],
                    brought=[order.asset({self.env.date: share})],
                )

            case "sell":
                if stocks := portfolio[order.asset]:
                    available_share = stocks[0].available(self.env.date).amount
                else:
                    available_share = 0

                if order.share:
                    share = order.share
                elif order.value:
                    share = int(order.value / price)
                else:
                    share = available_share

                if not self.allow_short and share > available_share:
                    logger.warning(f"没有足够的股数卖出({available_share}>{order.share}), 跳过卖出指令")
                    return None

                if self.round_lot:
                    share = share // 100 * 100

                return Result(
                    order=order,
                    sold=[order.asset({self.env.date: share})],
                    brought=[RMB(price * share)],
                )
            case _:
                raise ValueError(f"invalid order category: {order.category}")

    def liquidate_asset(self, asset: Stock, day: date, stage: BaseStage) -> RMB:
        df = self.api.query(
            self.start_date,
            self.end_date,
            [Field.ST_开盘价, Field.ST_收盘价],
            stock=Stock[asset.symbol]
        )

        liquidating_value = 0

        if not to_datetime(day) in df.index:
            for brought_day, brought_share in asset.share_position.items():
                nearest_day = df.index[df.index.searchsorted(to_datetime(day), side='left')]
                liquidating_value += df.at[nearest_day, Field.ST_开盘价] * brought_share
        else:
            for brought_day, brought_share in asset.share_position.items():
                if brought_day < day and stage.time <= time(9, 30):
                    liquidating_value += df.at[to_datetime(day), Field.ST_开盘价] * brought_share

                elif brought_day < day and stage.time <= time(15, 0):
                    liquidating_value += df.at[to_datetime(day), Field.ST_收盘价] * brought_share

                elif (brought_day < day and stage.time >= time(15, 0)) or brought_day == day:
                    pos = df.index.get_loc(to_datetime(day))  # 获取位置
                    next_day = df.index[pos + 1]  # 下一个位置的日期
                    liquidating_value += df.at[next_day, Field.ST_开盘价] * brought_share

                else:
                    raise ValueError(f"invalid brought day: {brought_day}")

        return liquidating_value

    def __init__(self, api: "BaseAPI", start_date: date, end_date: date, stage: type["BaseStage"], **kwargs):
        super().__init__(api, start_date, end_date, stage)

        self.allow_debt = kwargs.get("allow_debt", False)
        self.allow_short = kwargs.get("allow_short", False)
        self.round_lot = kwargs.get("round_lot", True)


__all__ = ["StockBrokerCN"]
