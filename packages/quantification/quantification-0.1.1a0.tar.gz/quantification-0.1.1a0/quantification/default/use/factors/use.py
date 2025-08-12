import pandas as pd

from quantification import Injection, Use

from .factor import BaseFactor, clear_cache


class FactorsInjection(Injection):
    name = 'factors'

    def __init__(self, **kwargs: type[BaseFactor]):
        self.factors = kwargs

    def __call__(self, **kwargs):
        df = pd.DataFrame(columns=["Stock"] + list(self.factors.keys()))
        trader = kwargs['trader']
        assert hasattr(trader, 'stocks'), \
            "只有采用股票池的trader可以使用use_factors"

        clear_cache()
        for stock in trader.stocks:
            row = {}
            for (factor_name, factor_class) in self.factors.items():
                calculate_params = {
                    **kwargs,
                    "stock": stock
                }
                row[factor_name] = factor_class.run(**calculate_params)

            row["Stock"] = stock
            df.loc[len(df)] = row
            clear_cache()

        return df


use_factors = Use(FactorsInjection)

__all__ = ["use_factors"]
