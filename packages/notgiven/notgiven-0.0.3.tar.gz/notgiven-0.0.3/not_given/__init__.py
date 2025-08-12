"""
Defines `NotGiven` and `NOT_GIVEN`, a sentinel singleton to distinguish between
omitted arguments and those explicitly set to None.

- `NOT_GIVEN`, the only instance of `NotGiven`, is a constant, marked `Final`.
- `NOT_GIVEN` is falsy (`bool(NOT_GIVEN)` is always False)
- Cannot instantiate or subclass `NotGiven`
- Pickling/unpickling, copying, and deepcopying `NOT_GIVEN` all result in the same value.
- `NOT_GIVEN` has no slots, so attributes may not be set on it.
- `NOT_GIVEN`'s string representation is `"NOT_GIVEN"`
"""

from notgiven import *
