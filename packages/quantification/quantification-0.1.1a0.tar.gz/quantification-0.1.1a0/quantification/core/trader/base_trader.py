from tqdm import tqdm
from typing import TypeVar, Generic, TYPE_CHECKING
from datetime import date, timedelta, datetime

import requests

from .query import Query
from .report import AssetData, OrderResultData, PeriodData, PointData, BenchmarkData, ReportData
from .portfolio import Portfolio
from .collector import Collector
from .base_order import Result, BaseOrder
from .base_stage import BaseStage
from ..asset.cash import RMB
from ..data.field import Field

from ..env import EnvGetter, Env
from ..logger import logger
from ..configure import config

if TYPE_CHECKING:
    from ..data import BaseAPI
    from ..asset import BaseBroker, BaseAsset
    from ..strategy import BaseStrategy

StrategyType = TypeVar("StrategyType", bound="BaseStrategy")


class BaseTrader(Generic[StrategyType]):
    def __init__(
            self,
            api: "BaseAPI",
            init_portfolio: Portfolio,
            start_date: date,
            end_date: date,
            padding: int,
            stage: type[BaseStage],
            strategy: StrategyType,
            brokers: list[type["BaseBroker"]],
            **kwargs
    ):
        self.api = api
        self.start_date = start_date
        self.end_date = end_date
        self.stage = stage
        self.strategy = strategy
        self.portfolio = init_portfolio
        self.brokers = [
            broker(api, start_date - timedelta(days=10), end_date + timedelta(days=10), stage, **kwargs)
            for broker in brokers
        ]
        self.query = Query(api, start_date - timedelta(days=padding), end_date)

        self.collector = Collector()
        self.env: Env = Env(date=self.start_date, time=next(iter(self.stage)).time)
        EnvGetter.getter = lambda: self.env

    def match_broker(self, asset: "type[BaseAsset]") -> "BaseBroker|None":
        for candidate_broker in self.brokers:
            if candidate_broker.matchable(asset):
                return candidate_broker

        return None

    @property
    def timeline(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            for current_stage in self.stage:
                self.env = Env(date=current_date, time=current_stage.time)
                self.collector.commence(current_date, current_stage, self.portfolio)
                yield current_date, current_stage
            current_date += timedelta(days=1)

    def run(self):
        for day, stage in self.timeline:
            logger.trace(f"==========日期:{day}===阶段:{stage}==========")
            params = {
                "day": day,
                "stage": stage,
                "portfolio": self.portfolio,
                "context": self.strategy.context,
                "query": self.query,
                "trader": self,
                "strategy": self.strategy
            }

            hooks = self.strategy.triggered(**params)
            logger.trace(f"触发的全部hooks:{hooks}")

            for hook in hooks:
                logger.trace(f"开始运行{hook}")
                gen = hook(**params)
                order: BaseOrder | None = None
                result: Result | None = None

                while True:
                    try:
                        order = gen.send(result) if order else next(gen)
                        logger.trace(f"{hook}发出Order:{order}, 开始匹配Broker")

                        assert isinstance(order, BaseOrder), f"只能yield Order, 实际为{type(order)}"

                        broker = self.match_broker(order.asset)

                        if not broker:
                            logger.warning(f"{order}没有对应broker, 忽略该order")
                            result = None
                            continue

                        logger.trace(f"{broker}开始处理:{order}")

                        if result := broker.execute_order(order, self.portfolio):
                            logger.trace(f"{broker}处理完成:{result}")
                            self.handle_result(result)
                        else:
                            logger.trace(f"{broker}跳过指令:{order}")

                    except StopIteration:
                        logger.trace(f"运行结束{hook}")
                        break

    def handle_result(self, result: Result):
        self.portfolio += result.brought
        self.portfolio -= result.sold
        self.collector.collect(result, self.portfolio)
        logger.trace(f"资产增加{result.brought}, 减少{result.sold}")

    def liquidate(self, asset: "BaseAsset", day: date, stage: "BaseStage") -> int:
        if isinstance(asset, RMB):
            return asset.amount

        if (broker := self.match_broker(asset.__class__)) is None:
            return -1

        return broker.liquidate_asset(asset, day, stage)

    def report(self, title: str, description: str, benchmark: str) -> ReportData:
        periods_data = []

        for shard in tqdm(self.collector.shards, "生成报告"):
            portfolios_data: list[AssetData] = []
            total_liquidating_value = 0
            for asset in shard.portfolio:
                liquidating_value = self.liquidate(asset, shard.day, shard.stage)
                total_liquidating_value += liquidating_value
                portfolios_data.append(AssetData.from_asset(asset, liquidating_value=liquidating_value))

            datetime_str = datetime.combine(shard.day, shard.stage.time).isoformat()
            periods_data.append(PeriodData(
                datetime=datetime_str,
                liquidating_value=total_liquidating_value,
                logs=logger.records.get(datetime_str, []),
                portfolios=portfolios_data,
                transactions=[OrderResultData.from_result(result) for result in shard.results]
            ))

        benchmark_points = [
            PointData(
                datetime=index.to_pydatetime().isoformat(),
                value=row[Field.IN_收盘点位]
            ) for index, row in self.api.query(
                start_date=self.start_date,
                end_date=self.end_date,
                fields=[Field.IN_收盘点位],
                index=benchmark,
            ).iterrows()
        ]

        return ReportData(
            title=title,
            description=description,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date.isoformat(),
            init_value=periods_data[0].liquidating_value,
            periods=periods_data,
            benchmark=BenchmarkData(
                name=benchmark,
                init_value=benchmark_points[0].value,
                points=benchmark_points
            )
        )

    @staticmethod
    def submit(report: ReportData):
        url = f"{config.genesis_api}/back/report/"

        print(f"Endpoint {url}")

        return requests.post(
            url=f"{config.genesis_api}/back/report/",
            headers={"Authorization": f"Token {config.genesis_token}"},
            data={
                "title": report.title,
                "description": report.description,
                "benchmark": [{"datetime": i.datetime, "value": i.value} for i in report.benchmark.points],
                "strategy": [{"datetime": i.datetime, "value": i.liquidating_value} for i in report.periods],
                "full_report": report.model_dump_json()
            },
        ).json()


__all__ = ["BaseTrader"]
