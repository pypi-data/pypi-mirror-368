from typing import Any, Literal, NoReturn, TypeGuard, TypeIs, Final, final

__all__ = [
    "NotGiven",
    "NOT_GIVEN",
    "is_given",
    "is_not_given",
    "is_given_guard",
    "is_not_given_guard",
]


@final
class NotGiven:
    """
    Sentinel singleton to distinguish between omitted keyword arguments
    and those explicitly set to None.
    """

    __slots__ = ()

    def __new__(cls) -> NoReturn:
        raise TypeError("Use the module-level NOT_GIVEN singleton")

    def __init_subclass__(cls, /, **_) -> None:
        raise TypeError("NotGiven may not be subclassed")

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self):
        return "NOT_GIVEN"

    def __reduce__(self):
        return (_get_not_given, ())


def _get_not_given() -> NotGiven:
    return NOT_GIVEN


NOT_GIVEN: Final[NotGiven] = object.__new__(NotGiven)


def is_given[T](value: T | NotGiven) -> TypeIs[T]:
    return value is not NOT_GIVEN


def is_not_given(value: Any) -> TypeIs[NotGiven]:
    return value is NOT_GIVEN


def is_given_guard[T](value: T | NotGiven) -> TypeGuard[T]:
    """Alternative to `is_given` annotated with TypeGuard."""
    return value is not NOT_GIVEN


def is_not_given_guard(value: Any) -> TypeGuard[NotGiven]:
    """Alternative to `is_not_given` annotated with TypeGuard."""
    return value is NOT_GIVEN
