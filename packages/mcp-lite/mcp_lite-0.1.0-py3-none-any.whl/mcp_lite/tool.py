import inspect
from typing import Callable
from dataclasses import dataclass


__all__ = ['Tool']


@dataclass
class Tool:
    name: str = ""
    description: str = ""
    is_async: bool = False
    func: Callable = None

    def __post_init__(self):
        if self.func is not None:
            actual_is_async = inspect.iscoroutinefunction(self.func)
            if self.is_async != actual_is_async:
                raise ValueError(
                    f"is_async={self.is_async} does not match "
                    f"function async status ({actual_is_async})"
                )
