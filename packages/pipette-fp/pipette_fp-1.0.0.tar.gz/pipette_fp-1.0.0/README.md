# pipette

`pipette` is a lightweight, expressive Python library designed to enable clean, functional-style data processing pipelines with intuitive syntax and powerful composition.

Note that due to the limitations of Python's static typing, some features may not provide type hints as expected. However, the library is designed to be flexible and easy to use, even without strict type enforcement.

---

## Features

`pipette` is currently in early development, but it already includes:
- Lazy evaluation for efficient data processing.
- Support for custom transformations using the `@pipette` decorator.
- Core functional utilities like `select`, `where`, `reduce`, `sort_by`, and more.
- Currying support for partial function application.
- Basic monad implementation for chaining operations with error handling.

---

## Installation

`pipette` can be installed via pip from the Python Package Index (PyPI):

```bash
pip install pipette-fp
```

Alternatively, you can install the latest development version of `pipette` directly from GitHub:

```bash
pip install git+https://github.com/chriso345/pipette
```

## Usage

`pipette` aims to make functional pipelines clear and concise.
```python
from pipette import where, select, into

data = [
    {"active": True, "value": 10},
    {"active": False, "value": 5},
    {"active": True, "value": 7},
]

result = (
    data
    | where(lambda x: x["active"])
    | select(lambda x: x["value"])
    | into(list)
)

print(result)  # Output: [10, 7]
```

Custom transformations can easily be added to extend functionality:
```python
from pipette import pipette

@pipette
def double(x):
    return builtins.map(lambda n: n * 2, x)

result = (
    [1, 2, 3, 4]
    | double
    | into(list)
)

print(result)  # Output: [2, 4, 6, 8]
```

### Curry

`pipette` provides a submodule for easy currying of functions:
```python
from pipette.curry import curry

@curry
def add(x: int, y: int) -> int:
    return x + y

result = add(2)(3)
print(result) # Output: 5

result = add(2)
print(result(3)) # Output: 5
```

Note, however, that python's static typing does not support currying and the type hints will error.

### Monads

`pipette` also includes a simple monad implementation for chaining operations:
```python
from pipette.monad import Maybe, Some, Nothing

def safe_divide(x, y) -> Maybe[float]:
    if y == 0:
        return Nothing()
    else:
        return Some(x / y)

s = Some(10) >> (lambda x: safe_divide(x, 2)) | (lambda x: x + 1)
print(s) # Output: Some(6.0)

n = Some(10) >> (lambda x: safe_divide(x, 0)) | (lambda x: x + 1)
print(n) # Output: Nothing
```

Here `>>` binds the monad value to the function, and `|` provides a simple way to map the result to another function.


---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
