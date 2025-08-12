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

from notgiven import *
