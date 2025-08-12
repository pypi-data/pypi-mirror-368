from datetime import date

from .portfolio import Portfolio
from .base_order import Result
from .base_stage import BaseStage


class Shard:
    def __init__(
            self,
            day: date,
            stage: BaseStage,
            portfolio: Portfolio,
    ):
        self.day = day
        self.stage = stage
        self.portfolio = portfolio
        self.results: list[Result] = []

    def collect(self, result: Result):
        self.results.append(result)

    def __repr__(self):
        return (
            f"================{self.day} {self.stage.time}================\n"
            f"Portfolio: {self.portfolio}\n"
            f"Results: {self.results}\n"
        )

    __str__ = __repr__


class Collector:
    def __init__(self):
        self.shards: list[Shard] = []

    def commence(
            self,
            day: date,
            stage: BaseStage,
            portfolio: Portfolio,
    ):
        self.shards.append(Shard(day, stage, portfolio.copy))

    def collect(self, result: Result, portfolio: Portfolio):
        self.shards[-1].collect(result)
        self.shards[-1].portfolio = portfolio.copy
