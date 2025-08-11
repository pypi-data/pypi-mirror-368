# GenAIMath

GenAIMath is a Python library for advanced mathematical operations using arbitrary-precision arithmetic. It provides functions for arithmetic, roots, powers, factorials, gamma function, logarithms, and more.

## Features
- Arbitrary-precision arithmetic
- Advanced mathematical functions
- Easy-to-use API

## Installation

You can install GenAIMath via pip (after publishing to PyPI):

```bash
pip install genaimath
```

## Usage

```python
from genaimath import AINumber, sqrt, cbrt, factorial, gamma, ln

a = AINumber("10")
b = AINumber("20")
print(f"{a} + {b} = {a + b}")
print(f"Square root of {a} = {sqrt(a)}")
print(f"Factorial of {a} = {factorial(a)}")
```

## Testing

Run tests with:

```bash
python -m unittest discover tests
```

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Author
SoftwareApkDev
