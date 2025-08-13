# MIT License
#
# Copyright (c) 2024-Present Shachar Kraus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Helper module for testing

Attributes:
    TEST_BITS_START (int): Fixed-point width to start from (inclusive) when testing.
                           Defaults to 1.\f
                           Can be set via the environment variable ``PYFIXED_TEST_BITS_START``.
    TEST_BITS_END (int): Fixed-point width to end at (inclusive) when testing. Defaults to 4.\f
                         Can be set via the environment variable ``PYFIXED_TEST_BITS_END``.
    TEST_INT_RANGE_SAMPLES (int): Number of integer and fixed-point samples to use when testing.
                                  Defaults to 0.\f
                                  A value of 0 will test all possible samples.\f
                                  Can be set via the environment variable
                                  ``PYFIXED_TEST_INT_RANGE_SAMPLES``.
    TEST_FLOAT_RANGE_SAMPLES (int): Number of floating-point samples to use when testing.
                                    Defaults to 128.\f
                                    A value of 0 will test all possible samples (usually 2**32).\f
                                    Can be set via the environment variable
                                    ``PYFIXED_TEST_FLOAT_RANGE_SAMPLES``.
    rounding_modes (dict): A dictionary containing all rounding
                           modes and their mpmath implementations
    PYTHON_FLOAT_RANGES (tuple): Floating-point ranges for :py:class:`!float`
    NUMPY_FLOAT_RANGES (tuple): Floating-point ranges for NumPy floats
    MPMATH_FLOAT_RANGES (tuple): Floating-point ranges for :py:class:`!mpmath.mpf`
    GMPY2_FLOAT_RANGES (tuple): Floating-point ranges for :py:class:`!gmpy2.mpfr` (if available)
    FLOAT_RANGES (tuple): A collection of common floating-point range generators for testing
    PYTHON_COMPLEX_RANGES (tuple): Floating-point ranges for :py:class:`!complex`
    NUMPY_COMPLEX_RANGES (tuple): Floating-point ranges for NumPy complex floats
    MPMATH_COMPLEX_RANGES (tuple): Floating-point ranges for :py:class:`!mpmath.mpc`
    GMPY2_COMPLEX_RANGES (tuple): Floating-point ranges for :py:class:`!gmpy2.mpc` (if available)
    COMPLEX_RANGES (tuple): A collection of common complex floating-point
                            range generators for testing
"""

import copy
import math
import mpmath
import numpy
import os
import pyfixed
import pytest
import sys
import typing

try:
    import gmpy2
except ImportError:
    pass


TEST_BITS_START = int(os.environ.get('PYFIXED_TEST_BITS_START', 1))
TEST_BITS_END = int(os.environ.get('PYFIXED_TEST_BITS_END', 4))
TEST_INT_RANGE_SAMPLES = int(os.environ.get('PYFIXED_TEST_INT_RANGE_SAMPLES', 0))
TEST_FLOAT_RANGE_SAMPLES = int(os.environ.get('PYFIXED_TEST_FLOAT_RANGE_SAMPLES', 128))


def iterator(*args):
    """Iterates arguments

    Args:
        ... : Values to iterate

    Yields:
        Next element
    """

    for x in args:
        yield x


def gmpy2_range(start: int, end: int | None = None, step: int = 1):
    """:py:func:`!range` for :py:class:`!gmpy2.mpz`

    Args:
        start (int, gmpy2.mpz): Start
        end (int, gmpy2.mpz, None, optional): End. Defaults to None.
        step (int, gmpy2.mpz, optional): Step. Defaults to 1.

    Raises:
        ValueError: step == 0

    Yields:
        gmpy2.mpz: Current number
    """

    if 'gmpy2' not in sys.modules:
        raise ModuleNotFoundError('No module named gmpy2')

    if end is None:
        end = start
        start = 0

    if step == 0:
        raise ValueError('step must be greater than 0')

    end = gmpy2.mpz(end)
    step = gmpy2.mpz(step)

    current = gmpy2.mpz(start)

    if step > 0:
        while current < end:
            yield current
            current += step
    else:
        while current > end:
            yield current
            current += step


def backend_range(*args, **kwargs):
    """:py:func:`!range` for :py:obj:`!pyfixed.backend`

    Args:
        start (pyfixed.backend): Start
        end (pyfixed.backend, None, optional): End. Defaults to None.
        step (pyfixed.backend, optional): Step. Defaults to 1.

    Yields:
        int, gmpy2.mpz: Next number
    """

    for i in (range if pyfixed.backend is int else gmpy2_range)(*args, **kwargs):
        yield i


def fixed_range(
        fraction_bits: int,
        integer_bits: int,
        sign: bool,
        saturation: bool,
        samples: int = -1
) -> pyfixed.Fixed:
    """Iterates over all fixed-point values

    Args:
        fraction_bits (int): Fraction bits
        integer_bits (int): Integer bits
        sign (bool): Signedness
        saturation (bool): Saturation
        samples (int): Number of samples to generate. Defaults to -1.
                       0 generates all possible samples.
                       -1 generates according to TEST_INT_RANGE_SAMPLES.

    Yields:
        pyfixed.Fixed: Next fixed-point number
    """

    max_magnitude = 1 << (fraction_bits + integer_bits)

    start = -max_magnitude if sign else 0
    end = max_magnitude  # Up to, excluding

    if samples == -1:
        samples = TEST_INT_RANGE_SAMPLES

    samples = min(end - start, samples)
    step = ((end - start) // samples) if samples else 1

    for i in backend_range(start, end, step):
        yield pyfixed.Fixed(
            value=i,
            fraction_bits=fraction_bits,
            integer_bits=integer_bits,
            sign=sign,
            saturation=saturation,
            internal=True
        )


def int_range(
        i_type: type,
        start: int | None = None,
        end: int | None = None,
        samples: int = -1,
        remove_invalid: bool = True
):
    """Iterates over integer values

    Args:
        i_type (type): Integer type
        start (int, None, optional): Range start.
                                     When not specified, defaults to the type's minimal value.
                                     If i_type is int, uses numpy.iinfo(int).min.
        end (int, None, optional): Range end.
                                   When not specified, defaults to the type's maximal value.
                                   If i_type is int, uses numpy.iinfo(int).max.
        samples (int): Number of samples to generate. Defaults to -1.
                       0 generates all possible samples.
                       -1 generates according to TEST_INT_RANGE_SAMPLES.
        remove_invalid (bool, optional): Remove invalid value (i.e. overflow). Defaults to True.

    Yields:
        Next number
    """

    if i_type is pyfixed.mpz_type:
        iinfo = numpy.iinfo(int)
    else:
        iinfo = numpy.iinfo(i_type)

    if start is None:
        start = int(iinfo.min)
    if end is None:
        end = int(iinfo.max) + 1

    if samples == -1:
        samples = TEST_INT_RANGE_SAMPLES

    samples = min(end - start, samples)
    step = ((end - start) // samples) if samples else 1

    if isinstance(i_type(), numpy.integer):
        for i in range(start, end, step):
            if i >= iinfo.min and i <= iinfo.max or not remove_invalid:
                yield i_type(i)
    elif i_type is int:
        # Yielding only for NumPy seems to mess up return values, so all ranges need to be yielded...
        for i in range(start, end, step):
            yield i
    elif i_type is pyfixed.mpz_type:
        if pyfixed.mpz_type is int:
            yield
        else:
            for i in gmpy2_range(start, end, step):
                yield i
    else:
        raise TypeError(f'Unsupported type {i_type}')


def float_range(f_type: type, samples: int = -1):
    """Creates a float range generator

    Args:
        f_type (type): Floating point type
        samples (int): Number of samples to generate. Defaults to -1.
                       0 generates all possible samples.
                       -1 generates according to TEST_FLOAT_RANGE_SAMPLES.

    Yields:
        Next number
    """

    finfo = numpy.finfo(f_type)

    float80 = f_type == numpy.float128 and finfo.nmant == 63 and finfo.iexp == 15

    # x86 platforms have 80-bit as their long double, while others might use float128
    actual_bits = 80 if float80 else finfo.bits

    total = 1 << actual_bits

    if samples == -1:
        samples = TEST_FLOAT_RANGE_SAMPLES

    samples = min(total, samples)
    step = (total // samples) if samples else 1

    width = math.ceil(finfo.bits / 8)

    for i in backend_range(0, total, step):
        # Cast in case f_type is float and not numpy.float
        result = f_type(
            numpy.frombuffer(
                i.to_bytes(width, byteorder='little'),
                dtype=f_type
            )[0]
        )
        if float80 and numpy.frexp(result)[1] >= \
                numpy.frexp(numpy.finfo(numpy.longdouble).smallest_normal)[1]:
            # Set the 1 bit (which isn't hidden, and leaving it clear creates NaN)
            yield f_type(
                numpy.frombuffer(
                    (i | (1 << 63)).to_bytes(width, byteorder='little'),
                    dtype=f_type)[0]
            )
        else:
            yield result


def cast_range(generator, constructor, *args, **kwargs):
    """Returns a generator which casts the results of a generator into another type

    Args:
        generator (function): Generator function
        constructor (function): Construction/casting/conversion function
        ... (optional): Arguments for the generator

    Yields:
        Next element
    """

    for x in generator(*args, **kwargs):
        yield constructor(x)


def complex_range(real_generator, constructor, *args, **kwargs):
    """Creates a complex range generator

    Args:
        real_generator (function): Real numbers generator function
        constructor (function): Complex numbers construction function
        ... (optional): Arguments for the real numbers generator

    Yields:
        Next number
    """

    for real in real_generator(*args, **kwargs):
        for imag in real_generator(*args, **kwargs):
            yield constructor(real, imag)


def operation_executer(lhs, rhs, op: str):
    """Runs the tested operator
    """

    if op == '__iadd__':
        res = copy.deepcopy(lhs)
        res += rhs
        return res
    elif op == '__add__':
        return lhs + rhs
    elif op == '__radd__':
        return rhs + lhs
    elif op == '__isub__':
        res = copy.deepcopy(lhs)
        res -= rhs
        return res
    elif op == '__sub__':
        return lhs - rhs
    elif op == '__rsub__':
        return rhs - lhs
    elif op == '__imul__':
        res = copy.deepcopy(lhs)
        res *= rhs
        return res
    elif op == '__mul__':
        return lhs * rhs
    elif op == '__rmul__':
        return rhs * lhs
    elif op == '__itruediv__':
        res = copy.deepcopy(lhs)
        res /= rhs
        return res
    elif op == '__truediv__':
        return lhs / rhs
    elif op == '__rtruediv__':
        return rhs / lhs
    elif op == '__ifloordiv__':
        res = copy.deepcopy(lhs)
        res //= rhs
        return res
    elif op == '__floordiv__':
        return lhs // rhs
    elif op == '__rfloordiv__':
        return rhs // lhs
    elif op == '__imod__':
        res = copy.deepcopy(lhs)
        res %= rhs
        return res
    elif op == '__mod__':
        return lhs % rhs
    elif op == '__rmod__':
        return rhs % lhs
    elif op == '__divmod__':
        return divmod(lhs, rhs)
    elif op == '__rdivmod__':
        return divmod(rhs, lhs)
    elif op == '__ilshift__':
        res = copy.deepcopy(lhs)
        res <<= rhs
        return res
    elif op == '__lshift__':
        return lhs << rhs
    elif op == '__irshift__':
        res = copy.deepcopy(lhs)
        res >>= rhs
        return res
    elif op == '__rshift__':
        return lhs >> rhs
    elif op == '__iand__':
        res = copy.deepcopy(lhs)
        res &= rhs
        return res
    elif op == '__and__':
        return lhs & rhs
    elif op == '__rand__':
        # This is a bug in gmpy2
        if getattr(type(rhs), '__module__', None) == 'gmpy2':
            return lhs.__rand__(rhs)
        return rhs & lhs
    elif op == '__ior__':
        res = copy.deepcopy(lhs)
        res |= rhs
        return res
    elif op == '__or__':
        return lhs | rhs
    elif op == '__ror__':
        # This is a bug in gmpy2
        if getattr(type(rhs), '__module__', None) == 'gmpy2':
            return lhs.__ror__(rhs)
        return rhs | lhs
    elif op == '__ixor__':
        res = copy.deepcopy(lhs)
        res ^= rhs
        return res
    elif op == '__xor__':
        return lhs ^ rhs
    elif op == '__rxor__':
        # This is a bug in gmpy2
        if getattr(type(rhs), '__module__', None) == 'gmpy2':
            return lhs.__rxor__(rhs)
        return rhs ^ lhs
    elif op == '__eq__':
        return lhs == rhs
    elif op == '__ne__':
        return lhs != rhs
    elif op == '__lt__':
        return lhs < rhs
    elif op == '__le__':
        return lhs <= rhs
    elif op == '__gt__':
        return lhs > rhs
    elif op == '__ge__':
        return lhs >= rhs
    elif op == '__req__':
        return rhs == lhs
    elif op == '__rne__':
        return rhs != lhs
    elif op == '__rlt__':
        return rhs < lhs
    elif op == '__rle__':
        return rhs <= lhs
    elif op == '__rgt__':
        return rhs > lhs
    elif op == '__rge__':
        return rhs >= lhs
    else:
        assert False


def behavior_check(
    error: str,
    operation,
    underflow_value: int = 0,
    undefined_value: tuple = (0, 0),
    check_values: bool = True
) -> None:
    """Checks different error behaviors

    Args:
        error (str): Error to check
        operation (any): Fixed-point operation to check
        underflow_value (int, optional): Value to which the operation underflows.
                                         Defaults to 0.
        undefined_value (tuple, optional): Tuple of values for undefined exceptions.
                                           Only relevant for complex numbers.
        check_values (bool, optional): Check returned values. Defaults to True.
    """

    others = [exception for exception in pyfixed.EXCEPTIONS_DICT.keys() if exception not in error]

    def check_retval():
        """Helper which checks returned values
        """

        val = operation()

        if not check_values:
            return

        if not isinstance(val, (list, tuple)):
            val = (val,)
        if 'overflow' in error:
            for v in val:
                if hasattr(v, 'real'):
                    assert v.real.value in (v._min_val, v._max_val)\
                        or v.imag.value in (v._min_val, v._max_val)
                else:
                    assert v.value in (v._min_val, v._max_val)
        elif 'underflow' in error:
            for v in val:
                if hasattr(v, 'real'):
                    assert v.real.value == underflow_value[0]
                    assert v.imag.value == underflow_value[1]
                else:
                    assert v.value == underflow_value
        elif 'undefined' in error:
            for v in val:
                if hasattr(v, 'real'):
                    assert v.real.value == undefined_value[0]
                    assert v.imag.value == undefined_value[1]
                else:
                    assert v.value == 0
        else:
            assert False, 'Unknown error'

    with pyfixed.with_partial_state(
        overflow_behavior=pyfixed.FixedBehavior.IGNORE,
        underflow_behavior=pyfixed.FixedBehavior.IGNORE,
        undefined_behavior=pyfixed.FixedBehavior.IGNORE
    ):
        # Check ignored behavior
        check_retval()
        assert pyfixed.get_sticky() == (False, False, False)
        # Check for an exception
        if isinstance(error, str):
            error = (error,)
        for e in error:
            with pyfixed.with_partial_state(**{f'{e}_behavior': pyfixed.FixedBehavior.RAISE}), \
                    pytest.raises(pyfixed.EXCEPTIONS_DICT[e]):
                operation()
        assert pyfixed.get_sticky() == (False, False, False)
        # Check the sticky bit
        with pyfixed.with_partial_state(
            **(
                dict.fromkeys(
                    [f'{e}_behavior' for e in error],
                    pyfixed.FixedBehavior.STICKY
                )
            )
        ):
            error_false = ((False,) * len(error)) if len(error) > 1 else False
            error_true = ((True,) * len(error)) if len(error) > 1 else True
            others_false = ((False,) * len(others)) if len(others) > 1 else False
            assert pyfixed.get_sticky(*error) == error_false
            assert pyfixed.get_sticky(*others) == others_false
            check_retval()
            assert pyfixed.get_sticky(*error) == error_true
            assert pyfixed.get_sticky(*others) == others_false
            # Check persistence
            operation()
            assert pyfixed.get_sticky(*error) == error_true
            assert pyfixed.get_sticky(*others) == others_false


class TestSuite(pyfixed.FixedConfig):
    """Test suite template class
    """

    tests: list | tuple
    """Collection of tests to run
    """

    def __init__(self, fraction_bits: int, integer_bits: int, sign: bool, saturation: bool):
        """Initializes the test suite

        Args:
            fraction_bits (int): Fixed-point fraction bits
            integer_bits (int): Fixed-point integer bits
            sign (bool): Fixed-point signedness
            saturation (bool): Fixed-point saturation
        """

        self.properties = pyfixed.get_fixed_properties(
            fraction_bits,
            integer_bits,
            sign,
            saturation
        )

    def __call__(self, idx: int = None) -> int:
        """Runs the test at index 'idx'

        Args:
            idx (int, optional): Test index.
                                 When not specified, returns the total number of runnable tests.

        Returns:
            int: Total number of runnable tests (when idx is None)
        """

        if idx is None:
            return len(self.tests)

        if isinstance(self.tests[idx], (tuple, list)):
            self.tests[idx][0](*(self.tests[idx][1:]))
        else:
            self.tests[idx]()


def mpmath_trunc(x: mpmath.mpf | mpmath.mpc) -> mpmath.mpf | mpmath.mpc:
    """Implements trunc for mpmath

    Args:
        x (mpmath.mpf, mpmath.mpc): Number to truncate

    Returns:
        mpmath.mpf, mpmath.mpc: trunc(x)
    """

    if isinstance(x, mpmath.mpc):
        return mpmath.mpc(mpmath_trunc(x.real), mpmath_trunc(x.imag))

    return (mpmath.floor if x >= 0 else mpmath.ceil)(x)


def mpmath_away(x: mpmath.mpf | mpmath.mpc) -> mpmath.mpf | mpmath.mpc:
    """Implements away for mpmath

    Args:
        x (mpmath.mpf, mpmath.mpc): Number to round away

    Returns:
        mpmath.mpf, mpmath.mpc: away(x)
    """

    if isinstance(x, mpmath.mpc):
        return mpmath.mpc(mpmath_away(x.real), mpmath_away(x.imag))

    return (mpmath.floor if x <= 0 else mpmath.ceil)(x)


def mpmath_half_down(x: mpmath.mpf | mpmath.mpc) -> mpmath.mpf | mpmath.mpc:
    """Implements rounding half down for mpmath

    Args:
        x (mpmath.mpf, mpmath.mpc): Number to round

    Returns:
        mpmath.mpf, mpmath.mpc: Rounded number
    """

    if isinstance(x, mpmath.mpc):
        return mpmath.mpc(mpmath_half_down(x.real), mpmath_half_down(x.imag))

    with mpmath.extraprec(1):
        return mpmath.floor(x + (0.5 if mpmath.frac(x) != 0.5 else 0))


def mpmath_half_up(x: mpmath.mpf | mpmath.mpc) -> mpmath.mpf | mpmath.mpc:
    """Implements rounding half up for mpmath

    Args:
        x (mpmath.mpf, mpmath.mpc): Number to round

    Returns:
        mpmath.mpf, mpmath.mpc: Rounded number
    """

    if isinstance(x, mpmath.mpc):
        return mpmath.mpc(mpmath_half_up(x.real), mpmath_half_up(x.imag))

    with mpmath.extraprec(1):
        return mpmath.floor(x + 0.5)


def mpmath_half_to_zero(x: mpmath.mpf | mpmath.mpc) -> mpmath.mpf | mpmath.mpc:
    """Implements rounding half to 0 for mpmath

    Args:
        x (mpmath.mpf, mpmath.mpc): Number to round

    Returns:
        mpmath.mpf, mpmath.mpc: Rounded number
    """

    if isinstance(x, mpmath.mpc):
        return mpmath.mpc(mpmath_half_to_zero(x.real), mpmath_half_to_zero(x.imag))

    return (mpmath_half_down if x >= 0 else mpmath_half_up)(x)


def mpmath_half_away(x: mpmath.mpf | mpmath.mpc) -> mpmath.mpf | mpmath.mpc:
    """Implements rounding half away from 0 for mpmath

    Args:
        x (mpmath.mpf, mpmath.mpc): Number to round

    Returns:
        mpmath.mpf, mpmath.mpc: Rounded number
    """

    if isinstance(x, mpmath.mpc):
        return mpmath.mpc(mpmath_half_away(x.real), mpmath_half_away(x.imag))

    return (mpmath_half_up if x >= 0 else mpmath_half_down)(x)


def mpmath_half_to_odd(x: mpmath.mpf | mpmath.mpc) -> mpmath.mpf | mpmath.mpc:
    """Implements rounding half to odd for mpmath

    Args:
        x (mpmath.mpf, mpmath.mpc): Number to round

    Returns:
        mpmath.mpf, mpmath.mpc: Rounded number
    """

    if isinstance(x, mpmath.mpc):
        return mpmath.mpc(mpmath_half_to_odd(x.real), mpmath_half_to_odd(x.imag))

    with mpmath.extraprec(1):
        return mpmath.floor(x + (0.5 if mpmath.frac(x / 2) * 2 != 1.5 else 0))


# Fixed-point rounding modes and their mpmath implementations
rounding_modes = {
    pyfixed.FixedRounding.FLOOR: mpmath.floor,
    pyfixed.FixedRounding.CEIL: mpmath.ceil,
    pyfixed.FixedRounding.TRUNC: mpmath_trunc,
    pyfixed.FixedRounding.AWAY: mpmath_away,
    pyfixed.FixedRounding.ROUND_HALF_DOWN: mpmath_half_down,
    pyfixed.FixedRounding.ROUND_HALF_UP: mpmath_half_up,
    pyfixed.FixedRounding.ROUND_HALF_TO_ZERO: mpmath_half_to_zero,
    pyfixed.FixedRounding.ROUND_HALF_AWAY: mpmath_half_away,
    pyfixed.FixedRounding.ROUND_HALF_TO_EVEN: mpmath.nint,
    pyfixed.FixedRounding.ROUND_HALF_TO_ODD: mpmath_half_to_odd,
}


def mpmath_divmod(
    a: mpmath.mpf,
    b: mpmath.mpf,
    mode: pyfixed.FixedRounding = pyfixed.FixedRounding.FLOOR
) -> tuple:
    """Implements divmod for mpmath

    Args:
        a (mpmath.mpf): Dividend
        b (mpmath.mpf): Divisor
        mode (pyfixed.FixedRounding, optional): Modulo rounding mode.
                                                Defaults to :py:obj:`!pyfixed.FixedRounding.FLOOR`.

    Returns:
        tuple: division result, remainder
    """

    if mode == pyfixed.FixedRounding.FLOOR:
        if mpmath.isinf(b):
            if a == 0:
                return mpmath.mpf(), mpmath.mpf()
            else:
                return a / b, (a if mpmath.sign(a) == mpmath.sign(b) else b)
        else:
            return mpmath.floor(a / b), a % b

    div = rounding_modes[mode](a / b)

    return div, a - div * b


def mpmath_nextafter(_from: mpmath.mpf, to: mpmath.mpf) -> mpmath.mpf:
    """Returns the next representable value after ``_from`` in the direction of ``to``

    Args:
        _from (mpmath.mpf): Value to start from
        to (mpmath.mpf): Value to go towards

    Returns:
        mpmath.mpf: Next value that's closer to ``to``
    """

    if mpmath.isnan(_from) or mpmath.isnan(to):
        return mpmath.nan

    if _from == to:
        return to

    # Note: normally nextafter can return the finite values
    # before/after infinities, but mpmath is unlimited
    if mpmath.isinf(_from):
        return _from

    f, e = mpmath.frexp(_from)
    f += mpmath.sign(to - _from) * mpmath.eps / 2
    return mpmath.ldexp(f, e)


def complex_ldexp(z: mpmath.mpc, e: int) -> mpmath.mpc:
    """Complex ldexp for mpmath

    Args:
        z (mpmath.mpc): Input
        e (int): Exponent

    Returns:
        mpmath.mpc: z * 2 ** e
    """

    e = int(e)

    return mpmath.mpc(
        mpmath.ldexp(z.real, e),
        mpmath.ldexp(z.imag, e)
    )


def complex_cmp(a: mpmath.mpc, b: mpmath.mpc, op: str) -> bool:
    """Implements unconventional comparisons for mpmath

    Args:
        a (mpmath.mpc): 1st operand
        b (mpmath.mpc): 2nd operand
        op (str): Comparison operation

    Returns:
        bool: Result
    """

    real_cmp = a.real - b.real
    imag_cmp = a.imag - b.imag

    if real_cmp and imag_cmp:
        return False  # Unordered
    elif real_cmp == 0 and imag_cmp == 0:
        return op in ('__le__', '__ge__')
    elif real_cmp:
        return (real_cmp > 0 and op in ('__gt__', '__ge__')) \
            or (real_cmp < 0 and op in ('__lt__', '__le__'))
    else:
        return (imag_cmp > 0 and op in ('__gt__', '__ge__')) \
            or (imag_cmp < 0 and op in ('__lt__', '__le__'))


def mpmath_bitwise(a: mpmath.mpf, b: mpmath.mpf, op) -> mpmath.mpf:
    """Calculates bitwise operations for mpmath.
       See https://en.wikipedia.org/wiki/Bitwise_operation#Mathematical_equivalents.

    Args:
        a (mpmath.mpf): LHS
        b (mpmath.mpf): RHS
        op (any): Operation to perform

    Returns:
        mpmath.mpf: Result
    """

    # Convert to semi-fixed and & matching bits

    a_mant, a_e, _ = pyfixed.semi_fixed(a)
    b_mant, b_e, _ = pyfixed.semi_fixed(b)
    a_e = -a_e
    b_e = -b_e

    diff = a_e - b_e
    if diff >= 0:
        a_mant <<= diff
    else:
        b_mant <<= -diff

    return mpmath.ldexp(op(a_mant, b_mant), min(a_e, b_e))


def mpmath_and(a: mpmath.mpf, b: mpmath.mpf) -> mpmath.mpf:
    """Calculates AND for mpmath.

    Args:
        a (mpmath.mpf): LHS
        b (mpmath.mpf): RHS

    Returns:
        mpmath.mpf: Result
    """

    return mpmath_bitwise(a, b, lambda a, b: a & b)


def mpmath_or(a: mpmath.mpf, b: mpmath.mpf) -> mpmath.mpf:
    """Calculates OR for mpmath.

    Args:
        a (mpmath.mpf): LHS
        b (mpmath.mpf): RHS

    Returns:
        mpmath.mpf: Result
    """

    return mpmath_bitwise(a, b, lambda a, b: a | b)


def mpmath_xor(a: mpmath.mpf, b: mpmath.mpf) -> mpmath.mpf:
    """Calculates XOR for mpmath.

    Args:
        a (mpmath.mpf): LHS
        b (mpmath.mpf): RHS

    Returns:
        mpmath.mpf: Result
    """

    return mpmath_bitwise(a, b, lambda a, b: a ^ b)


def run_tests(suite_class: type) -> typing.Callable:
    """Runs a test suite

    Args:
        suite_class (type): Suite class to run

    Returns:
        typing.Callable: Test runner

    Note:
        Runs tests on all possible fixed-point configurations
        of widths TEST_BITS_START to TEST_BITS_END
    """

    @pytest.mark.parametrize(
        'suite,test_idx',
        (
            (suite, test_idx)
            for suite in (
                # Test signed and unsigned types according to TEST_BITS_*
                suite_class(fraction_bits, integer_bits, sign, saturation)
                for saturation in (False, True)
                for sign in (False, True)
                for fraction_bits in range(0, TEST_BITS_END - sign + 1)
                for integer_bits in range(
                    max(TEST_BITS_START - fraction_bits - sign, 0),
                    TEST_BITS_END - sign - fraction_bits + 1
                )
            )
            for test_idx in range(suite())
        )
    )
    def runner(suite: suite_class, test_idx: int) -> None:
        suite(test_idx)

    return runner

# Common test ranges


def numpy_complex256(x=0, y=0) -> numpy.complex256:
    """Two-variable constructor for ``numpy.complex256``.
       Used because ``numpy.complex256`` doesn't support two-variable construction,
       e.g. ``numpy.complex256(1, 1)``, and because NumPy has a problem with multiplying
       large long double numbers with ``1j``.

    Args:
        x (any, optional): Real component. Defaults to 0.
        y (any, optional): Imaginary component. Defaults to 0.

    Returns:
        numpy.complex256: long double complex number
    """

    return numpy.complex256(x + 1j * y)


PYTHON_FLOAT_RANGES = (
    (float_range, float),
    (iterator, math.inf, -math.inf, math.nan),
)

NUMPY_FLOAT_RANGES = (
    (float_range, numpy.float32),
    (float_range, numpy.float64),
    (float_range, numpy.float128),
    (iterator, numpy.inf, -numpy.inf, numpy.nan),
)

MPMATH_FLOAT_RANGES = (
    (cast_range, float_range, mpmath.mpf, float),
    (iterator, mpmath.inf, -mpmath.inf, mpmath.nan),
)

GMPY2_FLOAT_RANGES = (
    (cast_range, float_range, pyfixed.mpfr_type, float)
    if pyfixed.mpfr_type is not float
    else None,
    (
        iterator,
        pyfixed.mpfr_type(math.inf),
        pyfixed.mpfr_type(-math.inf),
        pyfixed.mpfr_type(math.nan)
    )
    if pyfixed.mpfr_type is not float
    else None,
)

FLOAT_RANGES = PYTHON_FLOAT_RANGES + NUMPY_FLOAT_RANGES + MPMATH_FLOAT_RANGES + GMPY2_FLOAT_RANGES

PYTHON_COMPLEX_RANGES = (
    (complex_range, float_range, complex, float),
    (
        iterator,
        *(
            complex(r, i)
            for r in (1, math.inf, -math.inf, math.nan)
            for i in (1, math.inf, -math.inf, math.nan)
            if not math.isfinite(r) or not math.isfinite(i)
        )
    ),
)
NUMPY_COMPLEX_RANGES = (
    (complex_range, float_range, numpy.complex64, numpy.float32),
    (complex_range, float_range, numpy.complex128, numpy.float64),
    (
        complex_range,
        float_range,
        numpy_complex256,
        numpy.float64
    ),
    (
        iterator,
        *(
            numpy.complex128(r, i)
            for r in (1, numpy.inf, -numpy.inf, numpy.nan)
            for i in (1, numpy.inf, -numpy.inf, numpy.nan)
            if not numpy.isfinite(r) or not numpy.isfinite(i)
        )
    ),
)

MPMATH_COMPLEX_RANGES = (
    (complex_range, float_range, mpmath.mpc, float),
    (
        iterator,
        *(
            mpmath.mpc(r, i)
            for r in (1, mpmath.inf, -mpmath.inf, mpmath.nan)
            for i in (1, mpmath.inf, -mpmath.inf, mpmath.nan)
            if not mpmath.isfinite(r) or not mpmath.isfinite(i)
        )
    ),
)

GMPY2_COMPLEX_RANGES = (
    (complex_range, float_range, pyfixed.mpc_type, float)
    if pyfixed.mpfr_type is not float
    else None,
    (
        iterator,
        *(
            pyfixed.mpc_type(r, i)
            for r in (1, math.inf, -math.inf, math.nan)
            for i in (1, math.inf, -math.inf, math.nan)
            if not math.isfinite(r) or not math.isfinite(i)
        )
    )
    if pyfixed.mpfr_type is not float
    else None,

)

COMPLEX_RANGES = PYTHON_COMPLEX_RANGES + \
    NUMPY_COMPLEX_RANGES + \
    MPMATH_COMPLEX_RANGES + \
    GMPY2_COMPLEX_RANGES
