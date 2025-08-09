from functools import update_wrapper
from typing import Callable, TypeVar, final, Generic
from typing_extensions import override

_T = TypeVar("_T")
_U = TypeVar("_U")
_R = TypeVar("_R")


@final
class Curry(Generic[_R]):
    def __init__(
        self, func: Callable[..., _R], *args: object, **kwargs: object
    ) -> None:
        self.func: Callable[..., _R] = func
        self.args: tuple[object, ...] = args
        self.kwargs: dict[str, object] = kwargs
        _ = update_wrapper(self, func)

    def __call__(self, *args: object, **kwargs: object) -> _R | "Curry[_R]":
        new_args = self.args + args
        new_kwargs = {**self.kwargs, **kwargs}
        total_args = self._count_non_self_args()

        if len(new_args) + len(new_kwargs) >= total_args:
            return self.func(*new_args, **new_kwargs)
        return Curry(self.func, *new_args, **new_kwargs)

    @override
    def __repr__(self) -> str:
        name = getattr(self.func, "__name__", self.func.__class__.__name__)
        return f"curried::<{name}>(*{self.args}, **{self.kwargs})"

    def _count_non_self_args(self) -> int:
        code = self.func.__code__
        return code.co_argcount - (1 if "self" in code.co_varnames[:1] else 0)

    def __get__(self, instance: object, owner: type | None = None) -> "Curry[_R]":
        bound_func = self.func.__get__(instance, owner)  # type: ignore
        return Curry(bound_func, *self.args, **self.kwargs)


def curry(func: Callable[..., _R]) -> Curry[_R]:
    return Curry(func)
