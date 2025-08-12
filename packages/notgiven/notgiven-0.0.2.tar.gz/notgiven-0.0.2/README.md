## `NotGiven` and `NOT_GIVEN`

```
pip install notgiven
```

```python
from notgiven import (
    NotGiven,
    NOT_GIVEN,
    is_given,
    is_not_given,
    is_given_guard,
    is_not_given_guard,
)
```

### The details

- `NOT_GIVEN` is the only instance of `NotGiven`
- `NOT_GIVEN` is falsy (`if NOT_GIVEN` always returns False)
- Pickling/unpickling, copying, and deepcopying `NOT_GIVEN` all return the same value.
- `NOT_GIVEN`'s string representation is `"NOT_GIVEN"`
- `NOT_GIVEN` has no slots, so attributes may not be set on it.
- Cannot instantiate `NotGiven`
- Cannot subclass `NotGiven`
