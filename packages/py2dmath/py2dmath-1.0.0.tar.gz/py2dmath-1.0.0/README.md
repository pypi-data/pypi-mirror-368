# py2dmath

Simple calculation

## Features

- Provides efficient TEA decryption functionality, based on C implementation.
- Supports Python 3.6+

## Installation

Install the latest version of `py2dmath` from PyPI:

```bash
pip install py2dmath
```

## Usage
Here's how to use `py2dmath` for decryption:

```python
import py2dmath

curve = [0, 0, 0.5, 1]
count = 5
dec = py2dmath.getCurves(curve, count)
