from typing import Callable, TypeVar, final, Generic
from typing_extensions import override
from functools import update_wrapper

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


@final
class Pipette(Generic[T, U]):
    """
    Pipette is a functional programming utility class that allows for function pipelining.

    It can be used to create a chain of function calls, where the output of one function
    becomes the input to the next. This is particularly useful for composing functions
    in a readable and maintainable way.
    """

    def __init__(self, func: Callable[..., U], *args: object, **kwargs: object) -> None:
        self.args: tuple[object, ...] = args
        self.kwargs: dict[str, object] = kwargs
        self.func: Callable[..., U] = func
        _ = update_wrapper(self, func)

    def __ror__(self, other: T) -> U:
        return self.func(other, *self.args, **self.kwargs)

    def __call__(self, *args: object, **kwargs: object) -> "Pipette[T, U]":
        return Pipette(
            self.func,
            *self.args,
            *args,
            **self.kwargs,
            **kwargs,
        )

    @override
    def __repr__(self) -> str:
        name = getattr(self.func, "__name__", self.func.__class__.__name__)
        return f"piped::<{name}>(*{self.args}, **{self.kwargs})"

    def __get__(self, instance: object, owner: type | None = None) -> "Pipette[T, U]":
        bound_func = self.func.__get__(instance, owner)  # type: ignore
        return Pipette(bound_func, *self.args, **self.kwargs)


def pipette(func: Callable[..., U]) -> Pipette[object, U]:
    """
    Decorator to create a Pipette instance from a function.

    Parameters
    ----------
    func: Callable[..., U]
        The function to be wrapped in a pipette.
    Returns
    -------
    Pipette[object, U]
        A Pipette instance that can be used for function pipelining.

    Example
    -------
    >>> @pipette
    >>> def my_function(x: int, y: int) -> int:
    >>>    return x + y
    """
    return Pipette(func)
