from abc import ABC, abstractmethod
from typing import Callable, TypeVar, cast, final

from typing_extensions import override

from .monad import Monad

T = TypeVar("T")
U = TypeVar("U")


class Maybe(Monad[T], ABC):
    @abstractmethod
    def get_or_else(self, default: U) -> T | U: ...


@final
class Some(Maybe[T]):
    def __init__(self, value: T):
        self.value = value

    @override
    def map(self, func: Callable[[T], U]) -> Maybe[U]:
        return Some(func(self.value))

    @override
    def bind(self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return func(self.value)

    @override
    def get_or_else(self, default: U) -> T | U:
        return self.value

    @override
    def __repr__(self) -> str:
        return f"Some({self.value})"


@final
class Nothing(Maybe[T]):
    @override
    def map(self, func: Callable[[T], U]) -> Maybe[U]:
        return cast(Maybe[U], self)

    @override
    def bind(self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return cast(Maybe[U], self)

    @override
    def get_or_else(self, default: U) -> T | U:
        return default

    @override
    def __repr__(self) -> str:
        return "Nothing"
