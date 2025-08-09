from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Callable

T = TypeVar("T")
U = TypeVar("U")


class Monad(Generic[T], ABC):
    @abstractmethod
    def map(self, func: Callable[[T], U]) -> "Monad[U]": ...

    @abstractmethod
    def bind(self, func: Callable[[T], "Monad[U]"]) -> "Monad[U]": ...

    def __rshift__(self, fn: Callable[[T], "Monad[U]"]) -> "Monad[U]":
        """Alias for bind: monadic chaining with >>."""
        return self.bind(fn)

    def __or__(self, func: Callable[[T], U]) -> "Monad[U]":
        """Alias for map, allowing transformation of the value."""
        return self.map(func)
