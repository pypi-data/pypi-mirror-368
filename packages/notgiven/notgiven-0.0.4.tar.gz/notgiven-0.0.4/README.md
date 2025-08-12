# `NotGiven` and `NOT_GIVEN`

```
pip install notgiven
```

```python
from notgiven import (
    NotGiven,
    NOT_GIVEN,
    is_given,
    is_not_given,
    is_given_guard,  # Only useful in 3.13+
    is_not_given_guard,  # Only useful in 3.13+
)
```

### The details

- `NOT_GIVEN` is the only instance of `NotGiven`.
- `NotGiven` cannot be instantiated or subclassed.
- `NOT_GIVEN` is falsy (`bool(NOT_GIVEN)` is always False)
- Pickling/unpickling, copying, and deepcopying `NOT_GIVEN` all result in the same value.
- `NOT_GIVEN` has no slots, so attributes may not be set on it.
- `NOT_GIVEN`'s string representation is `"NOT_GIVEN"`
