import datetime
from abc import ABCMeta
from dataclasses import dataclass

from typing import Callable


@dataclass
class Env:
    date: datetime.date
    time: datetime.time


class EnvGetter(metaclass=ABCMeta):
    getter: Callable[[], Env] | None = None

    @property
    def env(self) -> Env | None:
        if self.__class__.getter is not None:
            return self.__class__.getter()

        return None


__all__ = ['EnvGetter', "Env"]
