import inspect
from abc import ABC, abstractmethod
from typing import Generator, Callable, TYPE_CHECKING

from ..util import inject

if TYPE_CHECKING:
    from ..trader import BaseOrder, Result

OrderGenerator = Generator["BaseOrder", "Result", None]
CommonFunc = Callable[..., None]
GeneratorFunc = Callable[..., OrderGenerator]
Func = CommonFunc | GeneratorFunc


class Injection(ABC):
    name: str

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        assert hasattr(cls, "name"), \
            "Injection类需要指定参数名"

        assert isinstance(cls.name, str), \
            "Injection指定的参数名必须为str"

    @abstractmethod
    def __call__(self, **kwargs):
        raise NotImplementedError


class Use:
    def __init__(self, injection: type[Injection]):
        self.injection = injection

    def __call__(self, *args, **kwargs):
        def wrapper(func: Func | WrappedFunc) -> WrappedFunc:
            wrapped_func = func if isinstance(func, WrappedFunc) else WrappedFunc(func)
            wrapped_func.register(self.injection(*args, **kwargs))
            return wrapped_func

        return wrapper


class WrappedFunc:
    def __init__(self, func: Func):
        self.func = func
        self.injections: list[Injection] = []

    def register(self, injection: Injection):
        self.injections.append(injection)

    def __call__(self, **kwargs):
        result = inject(self.func, **{
            **kwargs,
            **{injection.name: injection(**kwargs) for injection in self.injections}
        })
        return result if not inspect.isgenerator(result) else (yield from result)

    def __repr__(self) -> str:
        return f"<WrappedFunc {self.func.__name__}>"

    __str__ = __repr__


__all__ = ["Use", "Injection", "WrappedFunc", "Func"]
