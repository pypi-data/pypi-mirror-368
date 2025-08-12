from typing import Any

from .base_use import WrappedFunc, Func
from .base_trigger import Trigger


class Hook:
    def __init__(
            self,
            func: WrappedFunc,
            *,
            once: bool = False,
    ):
        self.func = func
        self.once = once
        self.triggered = False

    @property
    def active(self) -> bool:
        if self.once:
            return not self.triggered

        return True

    def __call__(self, **kwargs):
        self.triggered = True
        return self.func(**kwargs)

    def __repr__(self) -> str:
        return f"<Hook {self.func}>"

    __str__ = __repr__


class BaseStrategy:
    def __init__(self):
        self.context: dict[str, Any] = {}
        self.hooks: dict[Trigger, list[Hook]] = {}

    def on(self, trigger: Trigger, *, once: bool = False):
        def wrapper(func: Func | WrappedFunc) -> WrappedFunc:
            wrapped_func = func if isinstance(func, WrappedFunc) else WrappedFunc(func)

            if not self.hooks.get(trigger):
                self.hooks[trigger] = []

            self.hooks[trigger].append(Hook(wrapped_func, once=once))

            return wrapped_func

        return wrapper

    def triggered(self, **kwargs) -> list[Hook]:
        triggered_hooks: list[Hook] = []
        for trigger, hooks in self.hooks.items():
            if not trigger.fulfilled(**kwargs):
                continue

            for hook in hooks:
                if hook.active:
                    triggered_hooks.append(hook)

        return triggered_hooks


__all__ = ["BaseStrategy"]
