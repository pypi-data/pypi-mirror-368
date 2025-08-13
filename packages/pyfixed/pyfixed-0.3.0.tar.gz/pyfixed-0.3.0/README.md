# `pyfixed`

[![Latest Release](https://gitlab.com/ShacharKraus/pyfixed/-/badges/release.svg)](https://gitlab.com/ShacharKraus/pyfixed/-/releases) 

`pyfixed` is an arbitrary-precision fixed-point arithmetics library for Python.  
It currently is in early development.

`pyfixed` is licensed under the [MIT License](./LICENSE).

## Rational

`pyfixed` aims to aid in simulation of fixed-point arithmetics and testing of software and hardware solutions.  
It supports multiple configurations, with the goal of supporting a wide variety of hardware implementations.

`pyfixed` is currently *not* optimized, and has poor real-time performance.  
While optimizations are planned in general, the project does not aim to achieve any performance goals.

## Installation

Install latest:
```bash
pip3 install pyfixed
```

Build from source:
```bash
python -m build
pip3 install dist/*.whl
```

You can also use it directly by adding the root directory to your `PYTHONPATH`.

## Features

- `pyfixed.Fixed`: arbitrary-precision fixed-point.
  - Native API.
  - Simple arithmetic and bitwise operations.
  - 10 rounding modes (see `pyfixed.Fixed.FixedRounding`).
  - Optional exceptions on overflow, underflow and invalid operations (e.g. divide by 0).
    - Sticky exception flags.
  - Support for Python, NumPy and mpmath numeric types (integers and floats).
- `pyfixed.Complex`: arbitrary-precision complex fixed-point.
- `fixed_cmp`: visual comparison between fixed-point, IEEE-754 and posits.

### Planned Features

- Posit support (against [`softposit`](https://pypi.org/project/softposit/)).
- More functions:
  - $e^z$, $ln(z)$ and their derivatives.
  - FFT.
  - Matrix operations.
  - Other DSP-related operations.
