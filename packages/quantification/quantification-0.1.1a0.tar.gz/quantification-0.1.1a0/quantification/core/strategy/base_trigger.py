from abc import ABC, abstractmethod

from ..util import inject


class Condition(ABC):
    @abstractmethod
    def __call__(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    def settle(self, **kwargs):
        ...

    def __repr__(self):
        return f"Condition({self.name()})"

    __str__ = __repr__


class Trigger:
    def __init__(self, *conditions: Condition):
        self.conditions = conditions

    def fulfilled(self, **kwargs) -> bool:
        is_fulfilled = all([inject(condition, **kwargs) for condition in self.conditions])

        if not is_fulfilled:
            return False

        for condition in self.conditions:
            inject(condition.settle, **kwargs)

        return True

    def __and__(self, other):
        if other is None:
            return self

        if isinstance(other, Trigger):
            return Trigger(*self.conditions, *other.conditions)

        raise NotImplementedError(f"不支持合并条件{other}")

    def __rand__(self, other):
        if other is None:
            return self

        if isinstance(other, Trigger):
            return Trigger(*other.conditions, *self.conditions)

        raise NotImplementedError(f"不支持合并条件{other}")

    def __or__(self, other):
        raise NotImplementedError(f"不支持or运算")

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return f"<Trigger {self.conditions}>"

    __str__ = __repr__


__all__ = ["Trigger", "Condition"]
