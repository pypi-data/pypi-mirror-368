from datetime import date

import akshare as ak

from quantification import Condition, Trigger, cache_query, BaseStage


class EveryDay(Condition):
    def __call__(self):
        return True

    def name(self):
        return "每日"


class EveryNDay(Condition):
    def __init__(self, days: int):
        self.days = days
        self.pre_date: date | None = None

    def __call__(self, day: date) -> bool:
        if self.pre_date is None:
            return True

        if (day - self.pre_date).days >= self.days:
            return True

        return False

    def settle(self, day: date):
        self.pre_date = day

    def name(self):
        return f"每{self.days}日"


class EveryMonthNDay(Condition):
    def __init__(self, days: int):
        self.days = days
        self.triggered_date: date | None = None

    def __call__(self, day: date) -> bool:
        if self.triggered_date is None:
            return day.day >= self.days

        if self.triggered_date.month == day.month:
            return day < self.triggered_date

        self.triggered_date = None
        return day.day >= self.days

    def settle(self, day: date):
        self.triggered_date = day

    def name(self):
        return f"每月的第{self.days}日"


class TradeDay(Condition):
    def __call__(self, day: date):
        return day in cache_query()(ak.tool_trade_date_hist_sina)()["trade_date"].tolist()

    def name(self):
        return f"当为交易日"


class OnStage(Condition):
    def __init__(self, stage):
        self.stage = stage

    def __call__(self, stage: BaseStage):
        return bool(self.stage & stage)

    def name(self):
        return f"当stage为{self.stage}"


class T:
    每日 = Trigger(EveryDay())
    每N日 = lambda x: Trigger(EveryNDay(x))
    每月第N日 = lambda x: Trigger(EveryMonthNDay(x))
    交易日 = Trigger(TradeDay())
    交易阶段 = lambda x: Trigger(OnStage(x))


__all__ = ["T"]
