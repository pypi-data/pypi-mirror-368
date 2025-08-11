# DispatchBuilder

[![PyPI version](https://badge.fury.io/py/dispatchbuilder.svg)](https://badge.fury.io/py/dispatchbuilder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://github.com/kairos-xx/dispatchbuilder/actions/workflows/ci.yml/badge.svg)](https://github.com/kairos-xx/dispatchbuilder/actions)

DispatchBuilder is a lightweight runtime dispatch library for Python.
It lets you register multiple implementations for a single function or
method and automatically selects the best match at runtime based on
the argument types. This simplifies code that would otherwise rely
on long `if isinstance(...)` chains and makes your dispatch logic
explicit and maintainable.

## Features

- Simple, declarative registration of overloads with decorators.
- Dispatch on functions, instance methods, class methods, static
  methods, and property setters.
- Support for standard typing constructs: `Union`, `Optional`,
  `Literal`, generic containers (list, tuple, dict, set), and
  runtime‑checkable protocols.
- Heuristic specificity scoring to choose the most appropriate
  implementation.
- Caching of dispatch results for fast repeated calls.
- Zero external dependencies; works on Python 3.8 and newer.
- Comprehensive test suite and examples.

## Installation

Install the latest release from PyPI:

```bash
pip install dispatchbuilder
```

To install from source:

```bash
git clone https://github.com/kairos-xx/dispatchbuilder.git
cd dispatchbuilder
pip install -e .
```

## Quick Start

Here’s a minimal example showing how to use DispatchBuilder to
overload a function based on the type of its argument:

```python
from dispatchbuilder import dispatch

# Fallback implementation
def greet(name: object) -> str:
    return f"Hello, {name}!"

# Overload for strings
@dispatch.greet(name=str)
def _(name: str) -> str:
    return f"Hello, {name}, nice to meet you."

# Overload for integers
@dispatch.greet(name=int)
def _(name: int) -> str:
    return f"Hello, person #{name}."

print(greet("Alice"))  # Hello, Alice, nice to meet you.
print(greet(7))        # Hello, person #7.
print(greet(3.14))     # Hello, 3.14!
```

For more examples, including dispatching on multiple arguments,
methods, and property setters, see the [examples section](#usage-examples).

## Usage Examples

### Dispatch on Multiple Parameters

You can constrain more than one argument by specifying types via
keyword or positional arguments in the decorator:

```python
# Constrain both a and b
@dispatch.combine(a=int, b=str)
def _(a: int, b: str) -> str:
    return f"Int={a}, Str={b}"

# Constrain both with positional arguments
@dispatch.combine(int, int)
def _(a: int, b: int, c: object) -> str:
    return f"Two ints: {a}, {b} (c is unconstrained)"

# Base implementation (fallback)
def combine(a: object, b: object, c: object) -> str:
    return f"Generic {a}, {b}, {c}"
```

### Dispatch on Methods and Properties

Dispatch works seamlessly with instance methods, class methods,
static methods, and property setters:

```python
class Converter:
    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, val: object) -> None:
        self._value = val  # fallback setter

    @dispatch.value(value=int)
    def _(self, value: int) -> None:
        self._value = value * 10

    @dispatch.value(value=str)
    def _(self, value: str) -> None:
        self._value = int(value)

c = Converter()
c.value = 3
assert c.value == 30
c.value = "7"
assert c.value == 7
```

### Union, Literal, and Optional Types

DispatchBuilder supports standard typing constructs:

```python
from typing import Union, Optional, Literal

@dispatch.process(value=Union[int, float])
def _(value: Union[int, float]) -> str:
    return f"Number: {value}"

@dispatch.process(value=Literal[1, 2, 3])
def _(value: int) -> str:
    return f"Small number: {value}"

@dispatch.process(value=Optional[str])
def _(value: Optional[str]) -> str:
    return "No text" if value is None else f"Text: {value}"
```

## Documentation

Full documentation is included in this repository under the
`dispatchbuilder_wiki` directory. You can browse it locally or view
it online if hosted. The wiki covers:

- Installation instructions
- Quickstart guide
- Advanced usage and internals
- API reference
- Demos and how to run them
- Troubleshooting and FAQ

## Demos

A collection of demo scripts lives in the `demo` directory. To run
all demos sequentially, save the following script as `run_demos.py`
in the project root and execute it:

```python
#!/usr/bin/env python3
from pathlib import Path
from subprocess import run
from sys import executable


def run_all_demos() -> None:
    demo_dir:Path = Path(__file__).parent / "demo"
    for file in sorted(demo_dir.glob("*.py")):
        print(f"== Running {file.name} ==")
        run([executable, str(file)], check=True)


if __name__ == "__main__":
    run_all_demos()
```

## Contributing

Contributions are welcome! To report bugs or propose features,
open an issue on GitHub. If you'd like to contribute code:

1. Fork the repository and create a new branch for your feature or fix.
2. Write tests to cover your change.
3. Ensure all tests pass (`pytest`) and code is formatted with
   `black`.
4. Update documentation if necessary.
5. Submit a pull request with a clear description of your changes.

## License

DispatchBuilder is released under the MIT License. See the
`LICENSE` file for details.