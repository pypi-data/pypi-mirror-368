from typing import TYPE_CHECKING
from datetime import date, datetime

from ..env import EnvGetter

if TYPE_CHECKING:
    from ..data import BaseAPI

cache = {}


class Query(EnvGetter):
    def __init__(self, api: "BaseAPI", start_date: date, end_date: date):
        super().__init__()

        self.api = api
        self.start_date = start_date
        self.end_date = end_date

    def __call__(self, **kwargs):
        assert self.env is not None, "无法获取env"
        key = str(kwargs)

        params = {
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        params.update(kwargs)

        if key not in cache:
            cache[key] = self.api.query(**params)

        return cache[key].on(datetime.combine(self.env.date, self.env.time))


__all__ = ['Query']
