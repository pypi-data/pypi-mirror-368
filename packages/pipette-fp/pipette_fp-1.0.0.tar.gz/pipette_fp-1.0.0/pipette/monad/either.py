from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable, cast, final
from typing_extensions import override

from .monad import Monad

L = TypeVar("L")
R = TypeVar("R")
U = TypeVar("U")


class Either(Generic[L, R], Monad[R], ABC):
    @property
    @abstractmethod
    def value(self) -> L | R: ...

    def is_right(self) -> bool:
        return isinstance(self, Right)

    def is_left(self) -> bool:
        return isinstance(self, Left)

    @override
    def map(self, f: Callable[[R], U]) -> "Either[L, U]":  # pyright: ignore[reportIncompatibleMethodOverride]
        if self.is_right():
            return Right(f(cast(Right[L, R], self).value))
        return cast(Either[L, U], self)

    @override
    def bind(self, f: Callable[[R], "Either[L, U]"]) -> "Either[L, U]":  # pyright: ignore[reportIncompatibleMethodOverride]
        if self.is_right():
            return f(cast(Right[L, R], self).value)
        return cast(Either[L, U], self)

    @abstractmethod
    def unwrap(self) -> L | R: ...


@final
class Left(Either[L, R]):
    def __init__(self, value: L):
        self._value = value

    @property
    @override
    def value(self) -> L:
        return self._value

    @override
    def unwrap(self) -> L:
        return self._value

    @override
    def __repr__(self) -> str:
        return f"Left({self._value})"


@final
class Right(Either[L, R]):
    def __init__(self, value: R):
        self._value = value

    @property
    @override
    def value(self) -> R:
        return self._value

    @override
    def unwrap(self) -> R:
        return self._value

    @override
    def __repr__(self) -> str:
        return f"Right({self._value})"
