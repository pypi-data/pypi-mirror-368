"""
Defines `NotGiven` and `NOT_GIVEN`, a sentinel singleton to distinguish between
omitted arguments and those explicitly set to None.

- `NOT_GIVEN` is the only instance of `NotGiven`.
- `NotGiven` cannot be instantiated or subclassed.
- `NOT_GIVEN` is falsy (`bool(NOT_GIVEN)` is always False)
- Pickling/unpickling, copying, and deepcopying `NOT_GIVEN` all result in the same value.
- `NOT_GIVEN` has no slots, so attributes may not be set on it.
- `NOT_GIVEN`'s string representation is `"NOT_GIVEN"`
- Thread-safe in all situations.
"""

from typing import Literal, Final, final

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
    Sentinel singleton to distinguish between omitted arguments and those
    explicitly set to None. `NOT_GIVEN` is the only instance.
    """

    __slots__ = ()

    def __new__(cls):
        raise TypeError("Cannot instantiate NotGiven")

    def __init_subclass__(cls, /, **_):
        raise TypeError("Cannot subclass NotGiven")

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self):
        return "NOT_GIVEN"

    def __reduce__(self):
        return (_get_not_given, ())


def _get_not_given():
    return NOT_GIVEN


NOT_GIVEN: Final[NotGiven] = object.__new__(NotGiven)
"""
Constant to distinguish between omitted arguments and those explicitly
set to None. This is the only instance of `NotGiven`.
"""

import sys

if sys.version_info >= (3, 13):
    from typing import TypeGuard, TypeIs

    def is_given[T](value: T | NotGiven) -> TypeIs[T]:
        return value is not NOT_GIVEN

    def is_not_given(value: object) -> TypeIs[NotGiven]:
        return value is NOT_GIVEN

    def is_given_guard[T](value: T | NotGiven) -> TypeGuard[T]:
        """Alternative to `is_given` annotated with TypeGuard."""
        return value is not NOT_GIVEN

    def is_not_given_guard(value: object) -> TypeGuard[NotGiven]:
        """Alternative to `is_not_given` annotated with TypeGuard."""
        return value is NOT_GIVEN

elif sys.version_info >= (3, 10):
    from typing import TypeGuard, TypeVar

    T = TypeVar("T")

    def is_given(value: T | NotGiven) -> TypeGuard[T]:
        return value is not NOT_GIVEN

    def is_not_given(value: object) -> TypeGuard[NotGiven]:
        return value is NOT_GIVEN

    is_given_guard = is_given
    is_not_given_guard = is_not_given

else:

    def is_given(value: object):
        return value is not NOT_GIVEN

    def is_not_given(value: object):
        return value is NOT_GIVEN

    is_given_guard = is_given
    is_not_given_guard = is_not_given
