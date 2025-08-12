from quantification import (
    RMB,
    Stock,
    Portfolio,
    BaseTrader,
    StockBrokerCN
)


class AFactorTrader(BaseTrader):
    def __init__(
            self,
            api,
            start_date,
            end_date,
            stage,
            strategy,
            stocks: list[type[Stock]],
            init_cash: float = 100_000,
            padding: int = 0,
            **kwargs
    ):
        super().__init__(
            api,
            Portfolio(RMB(init_cash)),
            start_date,
            end_date,
            padding,
            stage,
            strategy,
            [StockBrokerCN],
            **kwargs
        )
        self.stocks = stocks


__all__ = ["AFactorTrader"]
