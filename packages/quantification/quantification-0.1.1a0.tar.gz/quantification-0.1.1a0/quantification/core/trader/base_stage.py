from enum import Flag
from datetime import time


class BaseStage(Flag):
    @property
    def time(self) -> time:
        raise NotImplementedError

    def __repr__(self):
        return self.name

    __str__ = __repr__


__all__ = ['BaseStage']
