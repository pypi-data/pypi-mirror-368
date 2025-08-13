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

"""Internal fixed-point implementation module

Attributes:
    mpz_type (type): Type representing gmpy2.mpz. Set to int when gmpy2 is not available.
    mpfr_type (type): Type representing gmpy2.mpfr. Set to float when gmpy2 is not available.
    mpc_type (type): Type representing gmpy2.mpc. Set to complex when gmpy2 is not available.
    backend (type): Integer backend. When mpmath uses gmpy2.mpz, pyfixed uses it as well.\f
                    Python's integer backend can be forced by setting the environment variable
                    ``PYFIXED_NOGMPY`` to be non-zero.
    EXCEPTIONS_DICT (dict): Converts exception names to exception classes
    DEFAULT_FIXED_STATE (FixedState): Default configuration of the fixed state
    fixed_tls (threading.local): TLS for this module
    pyfixed.fixed_tls.current_fixed_state (FixedState): The fixed state of the current thread
"""


import contextlib
import copy
import dataclasses
import enum
import functools
import math
import mpmath
import numpy
import os
import threading
from typing import Self
import warnings


mpz_type: type = int
mpfr_type: type = float
mpc_type: type = complex

try:
    import gmpy2
    mpz_type = gmpy2.mpz
    mpfr_type = gmpy2.mpfr
    mpc_type = gmpy2.mpc
except ImportError:
    pass

backend: type = int

if not os.environ.get('PYFIXED_NOGMPY', False) and mpmath.libmp.BACKEND == 'gmpy':
    backend = gmpy2.mpz

backend_zero = backend(0)
backend_one = backend(1)


def mpfr_prec() -> int:
    """Returns the precision of mpfr_type

    Returns:
        int: Precision
    """

    try:
        return gmpy2.get_context().precision
    except:
        return 53


def mpfr_to_mpf(x) -> mpmath.mpf:
    """Converts gmpy2.mpfr to mpmath.mpf

    Args:
        x (gmpy2.mpfr): Number to convert

    Returns:
        mpmath.mpf: Converted number

    Note:
        mpmath.mpf can't be used directly because gmpy2 stores invalid values in its _mpf_ field,
        e.g. ``gmpy2.mpfr(0)._mpf_ = (0, mpz(0), 1, 1)``
        and ``gmpy2.inf()._mpf_ = (0, mpz(0), -1073741823, 1)``
    """

    if gmpy2.is_finite(x):
        # Two problems:
        # 1. mpmath with the 'python' backend converts to float and then to mpf.
        # 2. gmpy2 has memory leaking issues.
        # Lucky for us, gmpy2.get_exp isn't leaking.

        e = gmpy2.get_exp(x) - gmpy2.get_context().precision
        mant = x * gmpy2.exp2(-e)
        return mpmath.ldexp(backend(mant), e)
    elif gmpy2.is_infinite(x):
        return mpmath.inf * gmpy2.sign(x)
    elif gmpy2.is_nan(x):
        return mpmath.nan
    else:
        raise ModuleNotFoundError('No module named gmpy2')


def mpc_to_mpc(x) -> mpmath.mpc:
    """Converts gmpy2.mpc to mpmath.mpc

    Args:
        x (gmpy2.mpc): Number to convert

    Returns:
        mpmath.mpc: Converted number
    """

    return mpmath.mpc(mpfr_to_mpf(x.real), mpfr_to_mpf(x.imag))


def float_is_inf(x) -> bool:
    """Generic function which checks if a float is plus/minus inf

    Args:
        x (any): Value to check

    Raises:
        TypeError: Unrecognized type

    Returns:
        bool: ``x == inf or x == -inf``
    """

    if isinstance(x, (float, complex, numpy.floating, numpy.complexfloating)):
        return numpy.isinf(x)
    elif isinstance(x, (mpmath.mpf, mpmath.mpc)):
        return mpmath.isinf(x)
    elif isinstance(x, (mpfr_type, mpc_type)):
        return gmpy2.is_infinite(x)
    elif isinstance(x, (int, numpy.integer, mpz_type)):
        return False
    else:
        raise TypeError()


def float_is_nan(x) -> bool:
    """Generic function which checks if a float is NaN

    Args:
        x (any): Value to check

    Returns:
        bool: ``x != x`` (True only for NaN)
    """

    return x != x


def float_is_fin(x) -> bool:
    """Generic function which checks if a float is finite

    Args:
        x (any): Value to check

    Raises:
        TypeError: Unrecognized type

    Returns:
        bool: x has a finite value
    """

    if isinstance(x, (float, complex, numpy.floating, numpy.complexfloating)):
        return numpy.isfinite(x)
    elif isinstance(x, (mpmath.mpf, mpmath.mpc)):
        return mpmath.isfinite(x)
    elif isinstance(x, (mpfr_type, mpc_type)):
        return gmpy2.is_finite(x)
    elif isinstance(x, (int, numpy.integer, mpz_type)):
        return True
    else:
        raise TypeError()

# Basic classes


class FixedRounding(enum.Enum):
    """Rounding modes.\f
       See https://en.wikipedia.org/wiki/Rounding#Rounding_to_integer.
    """

    FLOOR = enum.auto()
    """
    Round towards -inf
    """

    CEIL = enum.auto()
    """Round towards +inf
    """

    TRUNC = enum.auto()
    """Round towards 0
    """

    AWAY = enum.auto()
    """Round away from 0
    """

    ROUND_HALF_DOWN = enum.auto()
    """Round to nearest integer. Round half towards -inf.
    """

    ROUND_HALF_UP = enum.auto()
    """Round to nearest integer. Round half towards +inf.
    """

    ROUND_HALF_TO_ZERO = enum.auto()
    """Round to nearest integer. Round half towards 0.
    """

    ROUND_HALF_AWAY = enum.auto()
    """Round to nearest integer. Round half away from 0.
    """

    ROUND_HALF_TO_EVEN = enum.auto()
    """Round to nearest integer. Round half to even integer.
    """

    ROUND_HALF_TO_ODD = enum.auto()
    """Round to nearest integer. Round half to odd integer.
    """


class FixedBehavior(enum.Enum):
    """Behavior on error.
    """

    IGNORE = enum.auto()
    """Ignore the error
    """

    STICKY = enum.auto()
    """Toggle a sticky flag
    """

    RAISE = enum.auto()
    """Raise an exception
    """


@dataclasses.dataclass
class FixedState:
    """Fixed-point runtime state.
       Controls global fixed-point behavior.
       Default values match C floating point behavior.
    """

    rounding: FixedRounding = FixedRounding.ROUND_HALF_TO_EVEN
    """Rounding mode. Defaults to FixedRounding.ROUND_HALF_TO_EVEN.
    """

    overflow_behavior: FixedBehavior = FixedBehavior.RAISE
    """Behavior on overflow. Defaults to FixedBehavior.RAISE.
    """
    underflow_behavior: FixedBehavior = FixedBehavior.RAISE
    """Behavior on underflow. Defaults to FixedBehavior.RAISE.
    """
    undefined_behavior: FixedBehavior = FixedBehavior.RAISE
    """Behavior on undefined operation. Defaults to FixedBehavior.RAISE.
    """

    overflow_sticky: bool = False
    """Sticky flag which indicates that overflow occurred
    """
    underflow_sticky: bool = False
    """Sticky flag which indicates that underflow occurred
    """
    undefined_sticky: bool = False
    """Sticky flag which indicates an undefined operation
    """


class FixedOverflow(ArithmeticError):
    """Fixed-point overflow (saturation) exception
    """


class FixedUnderflow(ArithmeticError):
    """Fixed-point underflow (inaccurate) exception
    """


class FixedUndefined(ArithmeticError):
    """Fixed-point undefined (math error) exception
    """


EXCEPTIONS_DICT = {
    'overflow': FixedOverflow,
    'underflow': FixedUnderflow,
    'undefined': FixedUndefined
}

# Globals


# Provides the default state
DEFAULT_FIXED_STATE = FixedState()

# State management

# The thread-specific fixed state
fixed_tls = threading.local()
fixed_tls.current_fixed_state = copy.copy(DEFAULT_FIXED_STATE)


def get_fixed_state() -> FixedState:
    """Retrieves a copy of current thread's fixed state

    Returns:
        FixedState: State
    """

    return copy.copy(getattr(fixed_tls, 'current_fixed_state', DEFAULT_FIXED_STATE))


def set_fixed_state(state: FixedState) -> None:
    """Changes the current state

    Args:
        state (FixedState): New state
    """

    global fixed_tls

    fixed_tls.current_fixed_state = copy.copy(state)


@contextlib.contextmanager
def with_state(state: FixedState) -> FixedState:
    """Changes the current state within a 'with' block

    Args:
        state (FixedState): New state

    Yields:
        FixedState: New state
    """

    global fixed_tls

    old_state = get_fixed_state()
    fixed_tls.current_fixed_state = copy.copy(state)
    try:
        yield copy.copy(fixed_tls.current_fixed_state)
    finally:
        fixed_tls.current_fixed_state = old_state


def partial_state(
    rounding: FixedRounding = None,
    overflow_behavior: FixedBehavior = None,
    underflow_behavior: FixedBehavior = None,
    undefined_behavior: FixedBehavior = None,
    overflow_sticky: bool = None,
    underflow_sticky: bool = None,
    undefined_sticky: bool = None
) -> None:
    """Partially changes the current state

    Args:
        rounding (FixedRounding, optional): Rounding mode. Defaults to current mode.
        overflow_behavior (FixedBehavior, optional): Behavior on overflow.
                                                     Defaults to current behavior.
        underflow_behavior (FixedBehavior, optional): Behavior on underflow.
                                                      Defaults to current behavior.
        undefined_behavior (FixedBehavior, optional): Behavior on undefined.
                                                      Defaults to current behavior.
        overflow_sticky (bool, optional): Overflow sticky bit. Defaults to current value.
        underflow_sticky (bool, optional): Underflow sticky bit. Defaults to current value.
        undefined_sticky (bool, optional): Undefined sticky bit. Defaults to current value.

    Note:
        Sticky bits are cleared on write to behavior (even if the behavior didn't change)
    """

    global fixed_tls

    if not hasattr(fixed_tls, 'current_fixed_state'):
        set_fixed_state(DEFAULT_FIXED_STATE)

    if rounding is not None:
        fixed_tls.current_fixed_state.rounding = rounding

    if overflow_behavior is not None:
        fixed_tls.current_fixed_state.overflow_behavior = overflow_behavior
        fixed_tls.current_fixed_state.overflow_sticky = False
    if underflow_behavior is not None:
        fixed_tls.current_fixed_state.underflow_behavior = underflow_behavior
        fixed_tls.current_fixed_state.underflow_sticky = False
    if undefined_behavior is not None:
        fixed_tls.current_fixed_state.undefined_behavior = undefined_behavior
        fixed_tls.current_fixed_state.undefined_sticky = False

    if overflow_sticky is not None:
        fixed_tls.current_fixed_state.overflow_sticky = overflow_sticky
    if underflow_sticky is not None:
        fixed_tls.current_fixed_state.underflow_sticky = underflow_sticky
    if undefined_sticky is not None:
        fixed_tls.current_fixed_state.undefined_sticky = undefined_sticky


@contextlib.contextmanager
def with_partial_state(
    rounding: FixedRounding = None,
    overflow_behavior: FixedBehavior = None,
    underflow_behavior: FixedBehavior = None,
    undefined_behavior: FixedBehavior = None,
    overflow_sticky: bool = None,
    underflow_sticky: bool = None,
    undefined_sticky: bool = None
) -> FixedState:
    """Partially changes the current state within a 'with' block

    Args:
        rounding (FixedRounding, optional): Rounding mode. Defaults to current mode.
        overflow_behavior (FixedBehavior, optional): Behavior on overflow.
                                                     Defaults to current behavior.
        underflow_behavior (FixedBehavior, optional): Behavior on underflow.
                                                      Defaults to current behavior.
        undefined_behavior (FixedBehavior, optional): Behavior on undefined.
                                                      Defaults to current behavior.
        overflow_sticky (bool, optional): Overflow sticky bit. Defaults to current value.
        underflow_sticky (bool, optional): Underflow sticky bit. Defaults to current value.
        undefined_sticky (bool, optional): Undefined sticky bit. Defaults to current value.

    Yields:
        FixedState: New state

    Note:
        Sticky bits are cleared on write to behavior (even if the behavior didn't change)
    """

    global fixed_tls

    old_state = get_fixed_state()
    partial_state(
        rounding,
        overflow_behavior,
        underflow_behavior,
        undefined_behavior,
        overflow_sticky,
        underflow_sticky,
        undefined_sticky
    )
    try:
        yield copy.copy(fixed_tls.current_fixed_state)
    finally:
        fixed_tls.current_fixed_state = old_state


def get_sticky(*args, clear=False) -> bool | tuple:
    """Retrieves sticky bits and optionally clears them

    Args:
        ... (str, optional): Bit names to retrieve.
                   Can be 'overflow', 'underflow' and 'undefined'.
                   Defaults to all of them.
        clear (bool, optional): Clear retrieved bits. Defaults to False.

    Raises:
        ValueError: Invalid bit name

    Returns:
        bool, tuple: Bit value(s)

    Examples:
        get_sticky(): returns all sticky bits (overflow, underflow, undefined).
        get_sticky(clear=True): returns all sticky bits and clears them.
        get_sticky('overflow'): returns the overflow bit.
        get_sticky('overflow', 'underflow'): returns the overflow and underflow bits.
        get_sticky('underflow', 'overflow'): returns the underflow and overflow bits (in this order).
    """

    options = ('overflow', 'underflow', 'undefined')

    if len(args) == 0:
        args = options

    state = get_fixed_state()

    ret = []
    kwargs = {}
    for bit in args:
        if bit not in options:
            raise ValueError(f'Invalid bit name "{bit}"')

        key = bit + '_sticky'
        ret.append(state.__dict__[key])

        if clear:
            kwargs[key] = False

    if clear:
        partial_state(**kwargs)

    return tuple(ret) if len(ret) > 1 else ret[0]


def trigger_error(error: str, except_str: str = None) -> None:
    """For internal use only.
       Triggers an error.

    Args:
        error (str): Error name.
        except_str (str, optional): Exception string. Defaults to None.

    Raises:
        FixedOverflow: except_str
        FixedUnderflow: except_str
        FixedUndefined: except_str
    """

    behavior = get_fixed_state().__dict__[error + '_behavior']

    if behavior == FixedBehavior.RAISE:
        raise EXCEPTIONS_DICT[error](except_str)
    elif behavior == FixedBehavior.STICKY:
        partial_state(**{error + '_sticky': True})
    # else ignore


# Fixed


def float_round(x: mpmath.mpf, check_underflow: bool = True) -> mpmath.mpf:
    """Rounds a float

    Args:
        x (mpmath.mpf): Float to round
        check_underflow (bool, optional): Check for underflow. Defaults to True.

    Raises:
        FixedUnderflow: Result underflow

    Returns:
        mpmath.mpf: Result
    """

    result = x

    rounding = get_fixed_state().rounding

    if rounding == FixedRounding.CEIL                     \
            or (rounding == FixedRounding.TRUNC and x < 0)\
            or (rounding == FixedRounding.AWAY and x >= 0):
        result = mpmath.ceil(result)
        # For truncation, if x >= 0, floor will be used.
        # For away, if x < 0, floor will be used.
    else:
        with mpmath.extraprec(1):  # Required so that +0.5 is accurate
            if rounding == FixedRounding.ROUND_HALF_UP                         \
                    or (x < 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
                    or (x >= 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
                result += 0.5
            elif rounding == FixedRounding.ROUND_HALF_DOWN                      \
                    or (x >= 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
                    or (x < 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
                if result % 1 != 0.5:
                    result += 0.5
            elif rounding == FixedRounding.ROUND_HALF_TO_EVEN:
                if (result % 2) != 0.5:
                    result += 0.5
            elif rounding == FixedRounding.ROUND_HALF_TO_ODD:
                if (result % 2) != 1.5:
                    result += 0.5
            # else floor
            result = mpmath.floor(result)

    if check_underflow and result == 0 and x != 0:
        trigger_error('underflow')

    return result


def prepare_round(x: int, bit: int, rounding: FixedRounding = None) -> int:
    """Prepares a number for rounding via a floor operation

    Args:
        x (int): Number to prepare
        bit (int): Bit index where the number will be rounded at
        rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.

    Returns:
        int: Prepared number
    """

    if bit <= 0:
        return x

    if rounding is None:
        rounding = get_fixed_state().rounding

    half = backend_one << (bit - 1)
    one = backend_one << bit
    one_and_half_mask = (one << 1) - 1

    if rounding == FixedRounding.CEIL                     \
            or (rounding == FixedRounding.TRUNC and x < 0)\
            or (rounding == FixedRounding.AWAY and x >= 0):
        x += one - 1
        # For truncation, if x >= 0, floor will be used.
        # For away, if x < 0, floor will be used.
    elif rounding == FixedRounding.ROUND_HALF_UP                       \
            or (x < 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
            or (x >= 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
        x += half
    elif rounding == FixedRounding.ROUND_HALF_DOWN                      \
            or (x >= 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
            or (x < 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
        x += half - 1
    elif rounding == FixedRounding.ROUND_HALF_TO_EVEN:
        if (x & one_and_half_mask) != half:
            x += half
    elif rounding == FixedRounding.ROUND_HALF_TO_ODD:
        if (x & one_and_half_mask) != one + half:
            x += half
    # else floor

    return x


def shift_round(
    x: int,
    shift: int,
    rounding: FixedRounding = None,
    check_underflow: bool = True
) -> int:
    """Shifts (divides by a power of 2) with rounding

    Args:
        x (int): Number to divide
        shift (int): Bits to shift by. Shifts left (i.e. divides by 2 ** shift).
        rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.
        check_underflow (bool, optional): Check for underflow. Defaults to True.

    Raises:
        FixedUnderflow: Result underflow

    Returns:
        int: Result
    """

    if shift <= 0:
        return x << (-shift)

    result = prepare_round(x, shift, rounding=rounding) >> shift  # Floors
    if check_underflow and result == 0 and x != 0:
        trigger_error('underflow')

    return result


def div_round(
    dividend: int,
    divisor: int,
    rounding: FixedRounding = None,
    check_underflow: bool = True
) -> int:
    """Divides and rounds the result

    Args:
        dividend (int): Number to divide
        divisor (int): Number to divide by
        rounding (FixedRounding, optional): Rounding mode. Defaults to current's state's mode.
        check_underflow (bool, optional): Check for underflow. Defaults to True.

    Raises:
        FixedUndefined: Divide by 0
        FixedUnderflow: Result underflow

    Returns:
        int: Result
    """

    if divisor == 0:
        trigger_error('undefined', 'Divide by 0')
        return 0

    if rounding is None:
        rounding = get_fixed_state().rounding

    if divisor < 0:
        dividend = -dividend
        divisor = -divisor

    if divisor == 1:
        # No rounding required, and also breaks "epsilon = 1"
        return dividend

    half = divisor // 2

    result = dividend

    if rounding == FixedRounding.CEIL \
            or (rounding == FixedRounding.TRUNC and dividend < 0)\
            or (rounding == FixedRounding.AWAY and dividend >= 0):
        result += divisor - 1
        # For truncation, if dividend >= 0, floor will be used.
        # For away, if dividend < 0, floor will be used.
    elif rounding == FixedRounding.ROUND_HALF_UP                              \
            or (dividend < 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
            or (dividend >= 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
        result += half
    elif rounding == FixedRounding.ROUND_HALF_DOWN                             \
            or (dividend >= 0 and rounding == FixedRounding.ROUND_HALF_TO_ZERO)\
            or (dividend < 0 and rounding == FixedRounding.ROUND_HALF_AWAY):
        # This is result += half - (epsilon if divisor is even else 0)
        result += half - ((divisor & 1) ^ 1)
    elif rounding == FixedRounding.ROUND_HALF_TO_EVEN:
        if (dividend % (2 * divisor)) != half:
            result += half
    elif rounding == FixedRounding.ROUND_HALF_TO_ODD:
        if (dividend % (2 * divisor)) != 3 * divisor // 2:
            result += half
    # else floor

    result //= divisor  # Floors
    if check_underflow and result == 0 and dividend != 0:
        trigger_error('underflow')

    return result


def simulate_overflow(x: int, bits: int, sign: bool) -> int:
    """Simulates integer overflow

    Args:
        x (int): Integer input
        bits (int): Output bit width
        sign (bool): Output signedness

    Returns:
        int: ``x`` casted to the simulated integer type
    """

    int_limit = 1 << bits

    # Limit number to the given bits
    result = x & (int_limit - 1)
    # Simulate overflow to negative
    if sign and result >= (int_limit >> 1):
        result -= int_limit

    return result


def semi_fixed(x: mpmath.mpf) -> tuple:
    """Converts a float to a semi-fixed number

    Args:
        x (mpmath.mpf): Value to convert

    Returns:
        tuple:
        mantissa (int): Semi-fixed internal value.\f
        exp (int): Semi-fixed fraction bits.      \f
        e (int): Original exponent value.         \f
        mantissa / 2 ** exp = x                   \f
        mantissa / 2 ** mpmath.mp.prec * 2 ** e = x
    """

    # Convert to semi-fixed using frexp

    # frexp splits x to mantissa and exponent, where 0 <= mantissa < 1 or mantissa = 0:
    # x = mantissa * 2 ** exponent
    # We want the mantissa to be 0 <= mantissa < 2 ** (M + 1) (which is like fixed-point with M
    # fraction bits).
    #
    # Note that unless x = 0, the mantissa will always have the highest bit set (the always-1 bit).
    # So we want the range [2 ** M, 2 ** (M + 1)), representing numbers in [1, 2).
    # Achieving that is done via multiplication by 2 ** (M + 1):
    # 0.5 * 2 ** (M + 1) <= mantissa * 2 ** (M + 1) < 1 * 2 ** (M + 1)
    # 2 ** M <= mantissa * 2 ** (M + 1) < 2 ** (M + 1)
    # We then subtract 1 from the exponent to ensure that x = mantissa * 2 ** exponent.

    if x == 0:
        return 0, 0, 0

    M = mpmath.mp.prec

    m, e = mpmath.frexp(x)  # Returns [0.5, 1)
    e -= 1

    mantissa = backend(mpmath.ldexp(m, M + 1))
    exp = M - e

    return mantissa, exp, e


class FixedProperties:
    """Shared storage for fixed-point objects

    Note:
        All integer values MUST be :py:obj:`!int`, not :py:obj:`gmpy2.mpz`.

    Attributes:
        fraction_bits (int)
        integer_bits (int)
        sign (bool)
        _min_val (int)
        _max_val (int)
        half (int)
        one (int)
        human_format (str)
    """

    def __init__(self, fraction_bits: int, integer_bits: int, sign: bool, saturation: bool):
        """Initializes the properties class

        Args:
            fraction_bits (int): Number of fraction bits
            integer_bits (int): Number of integer bits
            sign (bool): Signedness
            saturation (bool): Saturation

        Raises:
            TypeError: Invalid argument types

        Note:
            Internal use only.
            Use get_fixed_properties instead.
        """

        # Initialize

        if not isinstance(fraction_bits, int):
            raise TypeError(f'`fraction_bits` must be `int`')
        if not isinstance(integer_bits, int):
            raise TypeError(f'`integer_bits` must be `int`')
        if not isinstance(sign, bool):
            raise TypeError(f'`sign` must be `int`')

        self.fraction_bits = fraction_bits
        self.integer_bits = integer_bits
        self.sign = sign
        self.saturation = saturation

        bits = self.fraction_bits + self.integer_bits

        self._min_val = -(backend_one << bits) if sign else 0
        self._max_val = (backend_one << bits) - 1
        self.epsilon = backend_one if bits else backend_zero
        self.half = (backend_one << (self.fraction_bits - 1)) if self.fraction_bits else 0
        self.one = backend_one << self.fraction_bits

        self.human_format = 'Fixed<'                     \
            f'{self.fraction_bits}, '                    \
            f'{self.integer_bits}, '                     \
            f'{"" if self.sign else "un"}signed, '       \
            f'{"" if self.saturation else "un"}saturated>'


@functools.cache
def get_fixed_properties(
        fraction_bits: int,
        integer_bits: int,
    sign: bool,
        saturation: bool
) -> FixedProperties:
    """Retrieves a FixedProperties class matching the given configuration

    Args:
        fraction_bits (int): Number of fraction bits
        integer_bits (int): Number of integer bits
        sign (bool): Signedness
        saturation (bool): Saturation

    Returns:
        FixedProperties: Properties

    Note:
        This function is cached
    """

    return FixedProperties(fraction_bits, integer_bits, sign, saturation)


class FixedConfig:
    """Base class containing fixed-point configuration properties

    Attributes:
        properties (FixedProperties): Format properties
    """

    @property
    def fraction_bits(self) -> int:
        """Class' number of fraction bits
        """

        return self.properties.fraction_bits

    @property
    def integer_bits(self) -> int:
        """Class' number of integer bits
        """

        return self.properties.integer_bits

    @property
    def sign(self) -> bool:
        """Class' signedness
        """

        return self.properties.sign

    @property
    def saturation(self) -> bool:
        """Class' saturation
        """

        return self.properties.saturation

    @property
    def precision(self) -> int:
        """Class' precision bits
        """

        return self.properties.fraction_bits + self.properties.integer_bits

    @property
    def bits(self) -> int:
        """Class' total bit width
        """

        return self.precision + self.sign

    @property
    def _min_val(self) -> int:
        """Internal representation of the smallest representable number
        """

        return self.properties._min_val

    @property
    def _max_val(self) -> int:
        """Internal representation of the largest representable number
        """

        return self.properties._max_val

    @property
    def epsilon(self) -> int:
        """Internal representation of the smallest positive non-zero representable number
        """

        return self.properties.epsilon

    @property
    def half(self) -> int:
        """Internal representation of 0.5
        """

        return self.properties.half

    @property
    def one(self) -> int:
        """Internal representation of 1

        Note:
            This value is unsaturated
        """

        return self.properties.one

    @property
    def human_format(self) -> str:
        """A human-readable fixed-point string representing this class
        """

        return self.properties.human_format


class Fixed(FixedConfig):
    """Fixed-point class

    Attributes:
        value (int): Internal value representing the actual value
    """

    def _set(self, value):
        """Sets the class' internal value according to the current settings

        Args:
            value: New value

        Raises:
            FixedOverflow: Value is out of the supported range (only if self.saturation is True)
        """

        if self.saturation:
            self.value = backend(max(min(value, self._max_val), self._min_val))

            if self.value != value:
                trigger_error(
                    'overflow',
                    f'Value "{value}" (internal) overflows out of {self.human_format}'
                )
        else:
            self.value = simulate_overflow(backend(value), self.bits, self.sign)

    def _create_same(self, value=None, internal: bool = True) -> Self:
        """Creates a fixed-point number of the same configuration as self

        Args:
            value (any, optional): Initial value. Defaults to None.
            internal (bool, optional): Value is the internal value. Defaults to True.

        Returns:
            Fixed: New fixed-point number
        """

        return Fixed(
            value,
            self.fraction_bits,
            self.integer_bits,
            self.sign,
            self.saturation,
            internal=internal
        )

    def _create_copy(self) -> Self:
        """Creates a copy of this number

        Returns:
            Fixed: Copy
        """

        return self._create_same(self.value)

    def _create_common(
            self,
            other: Self,
            value: int = None,
            internal: bool = False
    ) -> Self:
        """Creates a number in a common precision

        Args:
            other (Fixed): Other fixed
            value (int, optional): Initial value. Defaults to None.
            internal (bool, optional): Value is the internal value. Defaults to False.

        Returns:
            Fixed: Common precision number
        """

        return Fixed(
            value,
            fraction_bits=max(self.fraction_bits, other.fraction_bits),
            integer_bits=max(self.integer_bits, other.integer_bits),
            sign=self.sign or other.sign,
            saturation=self.saturation or other.saturation,
            internal=internal
        )

    def _common_copy(self, other: Self) -> Self:
        """Creates a copy of self in a common precision

        Args:
            other (Fixed): Other fixed

        Returns:
            Fixed: Common precision copy
        """

        return self._create_common(other, self)

    def _common_precision(self, other_val: int, other_prec: int, op, scale_back=True) -> int:
        """Performs an operation in common precision

        Args:
            other_val (int): Other integer value
            other_prec (int): Other value's precision (fraction bits)
            op (function): Operation to perform
            scale_back (bool, optional): Scale the result back to self's format. Defaults to True.

        Raises:
            FixedUnderflow: Underflow detected when converting to self's format

        Returns:
            int: Result
        """

        diff = self.fraction_bits - other_prec

        self_reg = self.value
        other_reg = other_val

        # Bring both to the same precision
        if diff < 0:
            self_reg <<= -diff
        else:
            other_reg <<= diff

        # Perform the operation
        result = op(self_reg, other_reg)

        # Scale if required
        if scale_back and diff < 0:
            result = shift_round(result, -diff)

        return result

    def _higher_precision(self) -> Self:
        """Creates a higher precision copy of this number

        Returns:
            Fixed: Higher precision copy
        """

        return promote(self)(self)

    def _to_generic_float(self, ldexp, prec: int):
        """Casts to a float

        Args:
            ldexp (function): Float's ldexp function
            prec (int): Float's precision (mantissa bits, including always-1)

        Returns:
            type(ldexp(0, 0)): Casted float
        """

        # Return self.value / 2 ** self.fraction_bits

        mantissa = self.value
        exponent = -self.fraction_bits
        mant_bits = mantissa.bit_length()

        if prec < mant_bits:
            # The mantissa won't fit in the format, so we remove LSBs via rounding.
            mantissa = shift_round(mantissa, mant_bits - prec, check_underflow=False)
            exponent += mant_bits - prec

        return ldexp(mantissa, int(exponent))

    def _floor(self) -> None:
        """Floors self
        """

        self.value &= -self.one

    def _handle_underflow_rounding(
        self,
        other: mpmath.mpf,
        rounding: FixedRounding = None,
        scale: int = 0
    ) -> None:
        """Handles rounding where self is added with a very small float

        Args:
            other (mpmath.mpf): Very small float
            rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.
            scale (int, optional): Scales (shifts) the number. Defaults to 0 (no scaling).

        Note:
            other's value is ignored, only the sign is taken into account
        """

        self._set(
            shift_round(
                (self.value << 2) + backend(mpmath.sign(other)),
                2,
                rounding=rounding,
                check_underflow=False
            ) << scale
        )

    def _div(
        self,
        other,
        rounded_bits: int = 0,
        rounding: FixedRounding = None,
        check_underflow: bool = True
    ) -> Self:
        """Divides self by a number

        Args:
            other (any): Divisor
            rounded_bits (int, optional): Bits to round, starting from LSB. Defaults to 0 (normal rounding).
            rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.
            check_underflow (bool, optional): Check for underflow. Defaults to True.

        Returns:
            Fixed: Result (self or NotImplemented)
        """

        def implementation(val: int, fract: int) -> None:
            # Shift left and divide

            # a / 2 ** N / (b / 2 ** M) = x / 2 ** N
            # a / b / 2 ** N * 2 ** M = x / 2 ** N
            # x = a / b * 2 ** M

            a = self.value
            b = val
            diff = fract - rounded_bits

            if diff >= 0:
                a <<= diff
            else:
                b <<= -diff

            self._set(
                div_round(
                    a,
                    b,
                    rounding=rounding,
                    check_underflow=check_underflow
                ) << rounded_bits
            )

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            # Cast NumPy integers to avoid overflow
            implementation(backend(other), 0)
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                return self._div(
                    mpmath.mpmathify(other),
                    rounded_bits=rounded_bits,
                    rounding=rounding,
                    check_underflow=check_underflow
                )
        elif isinstance(other, mpfr_type):
            # Match precisions
            with mpmath.workprec(mpfr_prec()):
                return self._div(
                    mpfr_to_mpf(other),
                    rounded_bits=rounded_bits,
                    rounding=rounding,
                    check_underflow=check_underflow
                )
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other):
                if check_underflow:
                    trigger_error(
                        'underflow',
                        f'Underflow: operation on {self.human_format} and {other}'
                    )
                self.value = backend_zero
            elif mpmath.isnan(other):
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                self.value = backend_zero
            elif other:  # Undefined if other == 0
                if self.value:
                    # Limits are similar to __iadd__ and __imul__:
                    #
                    # Overflow:
                    # |self / other| <= 2 ** integer_bits
                    # |other| >= |self| / 2 ** integer_bits
                    # Get the minimal value for |self| / 2 ** integer_bits
                    # by assigning |self| = 2 ** -fraction_bits:
                    # |other| >= 2 ** -fraction_bits * 2 ** -integer_bits
                    # |other| >= 2 ** -(fraction_bits + integer_bits)
                    #
                    # Underflow:
                    # |self / other| >= 2 ** -(fraction_bits + 1)
                    # |other| <= |self| * 2 ** (fraction_bits + 1)
                    # Get the maximal value for |self| / 2 ** (fraction_bits + 1)
                    # by assigning |self| = 2 ** integer_bits:
                    # |other| <= 2 ** integer_bits * 2 ** (fraction_bits + 1)
                    # |other| <= 2 ** (integer_bits + fraction_bits + 1)
                    #
                    # Final limits:
                    # 2 ** -(fraction_bits + integer_bits) <= |other| <= 2 ** (integer_bits + fraction_bits + 1)
                    # Using frexp, we get -fraction_bits - integer_bits <= exponent <= integer_bits + fraction_bits + 1

                    mantissa, exp, e = semi_fixed(other)

                    # -1 so rounding is handled properly
                    if self.saturation and e < -self.precision - 1:
                        trigger_error(
                            'overflow',
                            f'Overflow: 1 / {other} is too big for {self.human_format}'
                        )
                        # Silent overflow
                        self.value = backend(
                            self._max_val
                            if (self.value >= 0) == (other >= 0)
                            else self._min_val
                        )
                    # BUG Result could be infinite, e.g. 2 / 3, and won't be rounded correctly
                    # elif not self.saturation and exp > self.bits:
                    #     self.value = backend_zero
                    elif e > self.precision + 1:
                        if check_underflow:
                            trigger_error(
                                'underflow',
                                f'Underflow: 1 / {other} is too small for {self.human_format}'
                            )
                        # Silent underflow
                        sign = mpmath.sign(self.value) * mpmath.sign(other)
                        self.value = backend_zero
                        self._handle_underflow_rounding(sign, rounding=rounding, scale=rounded_bits)
                    else:
                        # Calculate like in fixed
                        implementation(mantissa, exp)
                else:
                    self.value = backend_zero
            else:
                trigger_error('undefined', 'Divide by 0')
                self.value = backend_zero
        else:
            return NotImplemented

        return self

    def _reverse_div(
        self,
        other,
        rounded_bits: int = 0,
        rounding: FixedRounding = None,
        check_underflow: bool = True
    ) -> Self:
        """Divides a number by self

        Args:
            other (any): Dividend
            rounded_bits (int, optional): Bits to round, starting from LSB. Defaults to 0 (normal rounding).
            rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.
            check_underflow (bool, optional): Check for underflow. Defaults to True.

        Returns:
            Fixed: Result (or NotImplemented)
        """

        # Note: other can't be Fixed

        def implementation(val: int, fract: int) -> Fixed:
            # a / 2 ** N / (b / 2 ** M) = x / 2 ** N
            # a / b / 2 ** N * 2 ** M = x / 2 ** N
            # x = a / b * 2 ** M

            a = self.value
            b = val
            diff = 2 * self.fraction_bits - fract - rounded_bits

            if diff <= 0:
                a <<= -diff
            else:
                b <<= diff

            return self._create_same(
                div_round(
                    b,
                    a,
                    rounding=rounding,
                    check_underflow=check_underflow
                ) << rounded_bits
            )

        if isinstance(other, Fixed):
            return NotImplemented
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            # Cast NumPy integers to avoid overflow
            return implementation(backend(other), 0)
        else:
            return NotImplemented

    def __init__(
        self,
        value:
            bool |
            int |
            float |
            complex |
            numpy.bool |
            numpy.integer |
            numpy.floating |
            numpy.complexfloating |
            mpmath.mpf |
            mpmath.mpc |
            Self
        = None,
        fraction_bits: int = None,
        integer_bits: int = None,
        sign: bool = None,
        saturation: bool = None,
        internal: bool = False
    ):
        """Initializes a new fixed-point number

        Args:
            value: Initial value. Defaults to None.
            fraction_bits (int, optional): Number of fraction bits. Defaults to 53.
            integer_bits (int, optional): Number of integer bits. Defaults to 10.
            sign (bool, optional): Signedness. Defaults to True.
            saturation (bool, optional): Saturation. Defaults to True.
            internal (bool, optional): Directly store the initial value. Defaults to False.

        Raises:
            TypeError:
                Invalid bit configuration
        """

        # Convert complex to real
        if hasattr(value, 'imag'):
            if value.imag != 0:
                warnings.warn(
                    numpy.exceptions.ComplexWarning(
                        'Casting complex values to real discards the imaginary part'
                    ),
                    stacklevel=2
                )
            value = value.real

        # Deduce configuration
        if fraction_bits is None:
            fraction_bits = value.fraction_bits if isinstance(value, Fixed) else 52
        if integer_bits is None:
            integer_bits = value.integer_bits if isinstance(value, Fixed) else 11
        if sign is None:
            sign = value.sign if isinstance(value, Fixed) else True
        if saturation is None:
            saturation = value.saturation if isinstance(value, Fixed) else True

        if fraction_bits < 0 or integer_bits < 0:
            raise TypeError("Bit amounts can't be negative")
        if fraction_bits + integer_bits + sign <= 0:
            raise TypeError('Fixed-point requires a non-zero number of bits')

        self.properties = get_fixed_properties(fraction_bits, integer_bits, sign, saturation)

        # Convert the value

        if value is None:
            self.value = backend_zero
            return

        if isinstance(value, Fixed):
            # Round and clip
            self._set(
                shift_round(
                    value.value,
                    0 if internal else (value.fraction_bits - self.fraction_bits)
                )
            )
        elif isinstance(value, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            # Cast to int because NumPy's integers are limited
            self._set(backend(value) << (0 if internal else self.fraction_bits))
        elif isinstance(value, (float, numpy.floating, mpmath.mpf, mpfr_type)):
            if float_is_inf(value):
                if self.saturation:
                    trigger_error('overflow', f'Initializing {self.human_format} from {value}')
                    self.value = backend(self._max_val if value > 0 else self._min_val)
                else:
                    self.value = backend_zero
                return
            elif float_is_nan(value):
                trigger_error('undefined', f'Initializing {self.human_format} from {value}')
                self.value = backend()
                return

            for t, p in (
                (float, numpy.finfo(numpy.float64).nmant + 1),

                (numpy.float32, numpy.finfo(numpy.float32).nmant + 1),
                (numpy.float64, numpy.finfo(numpy.float64).nmant + 1),
                # NumPy doesn't include the 1 bit, even for long double
                (numpy.float128, numpy.finfo(numpy.float128).nmant + 1),

                (mpmath.mpf, mpmath.mp.prec),

                (mpfr_type, mpfr_prec()),
            ):
                if isinstance(value, t):
                    prec = p
                    break

            with mpmath.workprec(prec):
                if mpfr_type is not float and isinstance(value, mpfr_type):
                    value = mpfr_to_mpf(value)

                self._set(
                    float_round(
                        mpmath.ldexp(
                            mpmath.mpmathify(value),
                            (0 if internal else self.fraction_bits)
                        )
                    )
                )

    # Conversions

    def __bool__(self) -> bool:
        """Converts to boolean

        Returns:
            bool: self != 0
        """

        return bool(self.value)

    def __int__(self) -> int:
        """Converts to Python integer

        Returns:
            int: round(self)

        Note:
            Ignores underflow
        """

        # Force cast to int in case backend is gmpy2.mpz
        return int(shift_round(self.value, self.fraction_bits, check_underflow=False))

    def __float__(self) -> float:
        """Converts to Python float

        Returns:
            float

        Note:
            Ignores underflow
        """

        return self._to_generic_float(math.ldexp, numpy.finfo(float).nmant + 1)

    def __complex__(self) -> complex:
        """Converts to Python complex

        Returns:
            complex: self + 0j

        Note:
            Ignores underflow
        """

        return complex(float(self))

    def __repr__(self) -> str:
        """Converts to a representation string

        Returns:
            str: Human format + value string
        """

        return f'{self.human_format}({str(self)})'

    def __str__(self) -> str:
        """Converts to string

        Returns:
            str: Fixed-point value in hex
        """

        return f'{hex(self.value)}p{-self.fraction_bits}'

    def __format__(self) -> str:
        """Converts to a string for formatting

        Returns:
            str: str(self)
        """

        return str(self)

    def __bytes__(self) -> bytes:
        """Converts to a byte string, which can be used directly in C

        Returns:
            bytes:
                Byte string, for the integer of type (u)intN,
                where N = fraction_bits + integer_bits + sign

        Note:
            Little endian
        """

        # Can't convert negative integers to bytes, so cast to the same type but unsigned
        return (
            simulate_overflow(self.value, self.bits, False)
            if self.sign
            else self.value
        ).to_bytes(
            length=(self.bits + 7) // 8,  # ceil(bits / 8)
            byteorder='little'
        )

    def __array__(self, dtype_meta=numpy.dtypes.Float64DType, copy: bool = True) -> numpy.ndarray:
        """Converts to NumPy

        Args:
            dtype_meta (numpy._DTypeMeta, optional): dtype meta from NumPy.
                                                     Defaults to double.
            copy (bool, optional) Create a copy.
                                  Defaults to True.

        Raises:
            TypeError: If copy == False

        Returns:
            numpy.ndarray: Converted value
        """

        dtype = dtype_meta.type

        if copy is False:
            raise TypeError(f'Casting Fixed to {dtype} requires creating a copy')

        if issubclass(dtype, numpy.complexfloating):
            dtype = type(numpy.real(dtype()))
        elif issubclass(dtype, numpy.integer):
            return numpy.array(dtype(int(self)))
        elif issubclass(dtype, numpy.bool):
            return numpy.array(numpy.bool(self.value))

        return numpy.array(
            self._to_generic_float(
                lambda x, p: numpy.ldexp(numpy.real(dtype(x)), p),
                numpy.finfo(dtype).nmant + 1
            )
        )

    @property
    def _mpf_(self) -> tuple:
        """Converts to mpmath tuple

        Returns:
            tuple: _mpf_ tuple
        """

        return self.mpmath()._mpf_

    def mpmath(self) -> mpmath.mpf:
        """Converts to mpmath.mpf

        Returns:
            mpmath.mpf: Converted value

        Note:
            Provided for compatibility with ComplexFixed
        """

        return self._to_generic_float(mpmath.ldexp, mpmath.mp.prec)

    def mpz(self):
        """Converts to gmpy2.mpz

        Returns:
            gmpy2.mpz: round(self)

        Note:
            Ignores underflow

        Note:
            Not implemented as ``__mpz__`` because :py:mod:`!gmpy2`
            will force conversion to :py:class:`!gmpy2.mpfr` when performing
            ``gmpy2.mpz() + pyfixed.Fixed()`` (instead of returning :py:class:`!pyfixed.Fixed`)
        """

        if mpz_type is int:
            raise ModuleNotFoundError('No module named gmpy2')

        return mpz_type(shift_round(self.value, self.fraction_bits, check_underflow=False))

    def mpfr(self):
        """Converts to gmpy2.mpfr

        Returns:
            gmpy2.mpfr: Converted value

        Note:
            Not implemented as ``__mpfr__`` because :py:mod:`!gmpy2`
            will force conversion to :py:class:`!gmpy2.mpfr` when performing
            ``gmpy2.mpz() + pyfixed.Fixed()`` (instead of returning :py:class`!pyfixed.Fixed`)
        """

        if mpfr_type is float:
            raise ModuleNotFoundError('No module named gmpy2')

        return self._to_generic_float(
            lambda x, e: x * gmpy2.exp2(e),
            mpfr_prec()
        )

    # Unary operators

    def __pos__(self) -> Self:
        """Creates a copy of self

        Returns:
            Fixed: Copy of self
        """

        return self._create_copy()

    def __neg__(self) -> Self:
        """Negates self

        Returns:
            Fixed: -self
        """

        return self._create_same(-self.value)

    def __invert__(self) -> Self:
        """One complement's negation of self

        Returns:
            Fixed: ~self
        """

        # Overflow is required, e.g. ~0 = 2 ** n - 1 for unsigned
        return self._create_same(simulate_overflow(~self.value, self.bits, self.sign))

    def __abs__(self) -> Self:
        """Calculates the absolute value (magnitude) of self

        Returns:
            Fixed: |self|
        """

        return self._create_copy() if self >= 0 else -self

    # Rounding

    def __floor__(self) -> int:
        """Rounds self towards -inf

        Returns:
            int: floor(self)

        Note:
            Ignores underflow
        """

        if self.fraction_bits:
            return int((self.value & -self.one) >> self.fraction_bits)
        else:
            return int(self.value)

    def __ceil__(self) -> int:
        """Rounds self towards +inf

        Returns:
            int: ceil(self)

        Note:
            Ignores underflow
        """

        if self.fraction_bits:
            return int(((self.value + self.one - self.epsilon) & -self.one) >> self.fraction_bits)
        else:
            return int(self.value)

    def __trunc__(self) -> int:
        """Rounds self towards 0

        Returns:
            int: trunc(self)

        Note:
            Ignores underflow
        """

        return math.floor(self) if self >= 0 else math.ceil(self)

    def __round__(self, ndigits: int = None) -> int | Self:
        """Rounds self

        Args:
            ndigits (int, optional): Round up to 'ndigits' digits after the point.
                                     Unlike conventional 'round', digits are binary.
                                     Defaults to None.

        Raises:
            FixedOverflow: When ndigits is not None and the result is outside the class' range

        Returns:
            int, Fixed:
            Rounded number as an integer when ndigits is None.\f
            Rounding number as a Fixed when ndigits != None (can be 0).

        Note:
            Ignores underflow
        """

        if ndigits is None:
            bit = self.fraction_bits
        else:
            if ndigits > self.fraction_bits:
                return self._create_copy()
            if ndigits < -self.precision:
                return self._create_same()
            bit = self.fraction_bits - ndigits

        mask = -(backend_one << bit)
        result = prepare_round(self.value, bit) & mask
        return int(result >> self.fraction_bits) if ndigits is None else self._create_same(result)

    # Binary operators

    # Addition

    def __iadd__(self, other) -> Self:
        """Adds a value to self in-place

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to add

        Returns:
            Fixed: self
        """

        if isinstance(other, Fixed):
            # Just add and clip
            self._set(self._common_precision(other.value, other.fraction_bits, lambda a, b: a + b))
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            # Like above, but it's not fixed.
            # Cast NumPy integers to avoid overflow.
            self._set(self.value + (backend(other) << self.fraction_bits))
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                self += mpmath.mpmathify(other)
        elif isinstance(other, mpfr_type):
            # Match precisions
            with mpmath.workprec(mpfr_prec()):
                self += mpfr_to_mpf(other)
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other):
                if self.saturation:
                    trigger_error(
                        'overflow',
                        f'Overflow: operation on {self.human_format} and {other}'
                    )
                    self.value = backend(self._max_val if other > 0 else self._min_val)
                # else do nothing
            elif mpmath.isnan(other):
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                self.value = backend_zero
            elif other:  # 0 has a negative infinity exponent
                # We limit other in order to pre-determine overflow and underflow.
                # We could just add, but with a float big enough, shifts will become very
                # expensive (double has an exponent [-1022, 1023], long double has even more,
                # and mpmath could be too much).
                #
                # The overflow limit is -(2 ** integer_bits) <= self + other <= 2 ** integer_bits.
                # (Should be < 2 ** integer_bits but it's insignificant).
                # We need a value self which lets other have a maximal magnitude.
                # This value is -sign(other) * 2 ** integer_bits, and we get:
                # -(2 ** integer_bits) <= other - sign(other) * 2 ** integer_bits <= 2 ** integer_bits
                # If other is positive:
                # -(2 ** integer_bits) <= other - (2 ** integer_bits) <= 2 ** integer_bits
                # 0 <= other <= 2 ** (integer_bits + 1)
                # Otherwise:
                # -(2 ** integer_bits) <= other + 2 ** integer_bits <= 2 ** integer_bits
                # -(2 ** (integer_bits + 1)) <= other <= 0
                # In general: |other| <= 2 ** (integer_bits + 1)
                #
                # The underflow limit is |self + other| >= 2 ** -fraction_bits.
                # We lower the limit by halving it so that exact halves are rounded
                # according to the rounding configuration.
                # We get |self + other| >= 2 ** -(fraction_bits + 1).
                # This time, we choose self = 0, because no other value can result
                # in underflow to 0 (unless other = -self, but that's not an underflow).
                # The limit is therefore |other| >= 2 ** -(fraction_bits + 1).
                #
                # Finally, our limits are
                # 2 ** -(fraction_bits + 1) <= |other| <= 2 ** (integer_bits + 1)
                # Using frexp, we get -fraction_bits - 1 <= exponent <= integer_bits + 1

                mantissa, exp, e = semi_fixed(other)

                if self.saturation and e > self.integer_bits + 1:
                    trigger_error(
                        'overflow',
                        f'Overflow: {other} is too big for {self.human_format}'
                    )
                    # Just clip it
                    self.value = backend(self._max_val if other >= 0 else self._min_val)
                elif not self.saturation and -exp > self.bits:
                    # do nothing (other overflows to 0)
                    pass
                elif e < -self.fraction_bits - 1:
                    # Guaranteed underflow
                    trigger_error(
                        'underflow',
                        f'Underflow: {other} is too small for {self.human_format}'
                    )
                    # Either sticky or ignored, so we need to round properly
                    self._handle_underflow_rounding(other)
                else:
                    # Treat it like a fixed
                    self._set(self._common_precision(mantissa, exp, lambda a, b: a + b))
        else:
            return NotImplemented

        return self

    def __add__(self, other):
        """Adds self and a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to add

        Returns:
            Result
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
            return result.__iadd__(other)
        elif isinstance(other, float):
            return float(self) + other
        elif isinstance(other, numpy.floating):
            return type(other)(self) + other
        elif isinstance(other, mpfr_type):
            return self.mpfr() + other
        else:
            return NotImplemented

    def __radd__(self, other):
        """Adds a value and self

        Args:
            other (bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to add

        Returns:
            Result
        """

        if isinstance(other, Fixed):
            return NotImplemented

        return self + other

    # Subtraction

    def __isub__(self, other) -> Self:
        """Subtracts a value from self in-place

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to subtract

        Returns:
            Fixed: self
        """

        if isinstance(other, Fixed):
            # Just subtract and clip
            self._set(self._common_precision(other.value, other.fraction_bits, lambda a, b: a - b))
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            # Like above, but it's not fixed.
            # Cast NumPy integers to avoid overflow.
            self._set(self.value - (backend(other) << self.fraction_bits))
        elif isinstance(other, (float, numpy.floating, mpmath.mpf, mpfr_type)):
            self += -other
        else:
            return NotImplemented

        return self

    def __sub__(self, other):
        """Subtracts self and a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to subtract

        Returns:
            Result
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
            return result.__isub__(other)
        elif isinstance(other, float):
            return float(self) - other
        elif isinstance(other, numpy.floating):
            return type(other)(self) - other
        elif isinstance(other, mpfr_type):
            return self.mpfr() - other
        else:
            return NotImplemented

    def __rsub__(self, other):
        """Subtracts a value and self

        Args:
            other (bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to subtract from

        Returns:
            Result
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            # Create an intermediate representation and subtract
            return self._create_same((backend(other) << self.fraction_bits) - self.value)
        elif isinstance(other, float):
            return other - float(self)
        elif isinstance(other, numpy.floating):
            return other - type(other)(self)
        elif isinstance(other, mpfr_type):
            return other - self.mpfr()
        else:
            return NotImplemented

    # Multiplication

    def __imul__(self, other) -> Self:
        """Multiplies self by a value in-place

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to multiply by

        Returns:
            Fixed: self
        """

        def implementation(val: int, fract: int) -> None:
            # Multiply bits and shift accordingly

            # a / 2 ** N * b / 2 ** M = x / 2 ** N
            # a * b / 2 ** (N + M) = x / 2 ** N
            # x = ab / 2 ** M

            self._set(shift_round(self.value * val, fract))

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            # Cast NumPy integers to avoid overflow.
            # Also optimize by avoiding shift_round.
            self._set(self.value * backend(other))
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                self *= mpmath.mpmathify(other)
        elif isinstance(other, mpfr_type):
            # Match precisions
            with mpmath.workprec(mpfr_prec()):
                self *= mpfr_to_mpf(other)
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other) and self.value != 0:
                if self.saturation:
                    trigger_error(
                        'overflow',
                        f'Overflow: operation on {self.human_format} and {other}'
                    )
                    self.value = backend(
                        self._max_val
                        if (other > 0) == (self.value > 0)
                        else self._min_val
                    )
                else:
                    self.value = backend_zero
            elif not mpmath.isfinite(other):
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                self.value = backend_zero
            elif self.value and other:  # Avoid zeros
                # Limit calculation - same concept as __iadd__, different calculation:
                #
                # The overflow limit is |self * other| <= 2 ** integer_bits.
                # We choose the minimal value for |self|, which is 2 ** -fraction_bits.
                # We get 2 ** -fraction_bits * |other| <= 2 ** integer_bits,
                # |other| <= 2 ** (fraction_bits + integer_bits).
                #
                # The underflow limit is |self * other| >= 2 ** -(fraction_bits + 1)
                # (with the +1 being for rounding halves).
                # We choose the maximal value for |self|, which is 2 ** integer_bits.
                # Now we get 2 ** integer_bits * |other| >= 2 ** -(fraction_bits + 1):
                # |other| >= 2 ** -(fraction_bits + integer_bits + 1).
                #
                # Finally, our limits are
                # 2 ** -(fraction_bits + integer_bits + 1) <= |other| <= 2 ** (fraction_bits + integer_bits).
                # Using frexp, we get -fraction_bits - integer_bits - 1 <= exponent <= fraction_bits + integer_bits

                mantissa, exp, e = semi_fixed(other)

                if e < -self.precision - 1:
                    trigger_error(
                        'underflow',
                        f'Underflow: {other} is too small for {self.human_format}'
                    )
                    # Silent underflow
                    sign = mpmath.sign(self.value) * mpmath.sign(other)
                    self.value = backend_zero
                    self._handle_underflow_rounding(sign)
                elif self.saturation and e > self.precision:
                    trigger_error(
                        'overflow',
                        f'Overflow: {other} is too big for {self.human_format}'
                    )
                    # Silent overflow
                    self.value = backend(
                        self._max_val
                        if (self.value >= 0) == (other >= 0)
                        else self._min_val
                    )
                elif not self.saturation and -exp > self.bits:
                    self.value = backend_zero
                else:
                    # Calculate like in fixed
                    implementation(mantissa, exp)
            else:
                self.value = backend_zero
        else:
            return NotImplemented

        return self

    def __mul__(self, other):
        """Multiplies self with a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to multiply by

        Returns:
            Result
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
            return result.__imul__(other)
        elif isinstance(other, float):
            return float(self) * other
        elif isinstance(other, numpy.floating):
            return type(other)(self) * other
        elif isinstance(other, mpfr_type):
            return self.mpfr() * other
        else:
            return NotImplemented

    def __rmul__(self, other):
        """Multiplies a value by self

        Args:
            other (bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to multiply

        Returns:
            Result
        """

        if isinstance(other, Fixed):
            return NotImplemented

        return self * other

    # Division

    def __itruediv__(self, other) -> Self:
        """Divides self by a value in-place

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Divisor

        Returns:
            Fixed: self
        """

        return self._div(other)

    def __truediv__(self, other):
        """Divides self by a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Divisor

        Returns:
            Result
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
            return result.__itruediv__(other)
        elif isinstance(other, float):
            return float(self) / other
        elif isinstance(other, numpy.floating):
            return type(other)(self) / other
        elif isinstance(other, mpfr_type):
            return self.mpfr() / other
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        """Divides a value by self

        Args:
            other (bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Dividend

        Returns:
            Result.
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            return self._reverse_div(other)
        elif isinstance(other, float):
            return other / float(self)
        elif isinstance(other, numpy.floating):
            return other / type(other)(self)
        elif isinstance(other, mpmath.mpf):
            return other / self.mpmath()
        elif isinstance(other, mpfr_type):
            return other / self.mpfr()
        else:
            return NotImplemented

    # Floor division (//)

    def __ifloordiv__(self, other) -> Self:
        """Divides self by a value and floors the result in-place

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Divisor

        Returns:
            Fixed: self

        Note:
            Underflow isn't raised
        """

        return self._div(
            other,
            rounded_bits=self.fraction_bits,
            rounding=FixedRounding.FLOOR,
            check_underflow=False
        )

    def __floordiv__(self, other):
        """Divides self by a value and floors the result

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Divisor

        Returns:
            Result

        Note:
            Underflow isn't raised
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
            return result.__ifloordiv__(other)
        elif isinstance(other, float):
            return float(self) // other
        elif isinstance(other, numpy.floating):
            return type(other)(self) // other
        elif isinstance(other, mpmath.mpf):
            # mpmath doesn't support //
            return mpmath.floor(self / other)
        elif isinstance(other, mpfr_type):
            return self.mpfr() // other
        else:
            return NotImplemented

    def __rfloordiv__(self, other):
        """Divides a value by self and floors the result

        Args:
            other (bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Dividend

        Returns:
            Fixed: self

        Note:
            Underflow isn't raised
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            return self._reverse_div(
                other,
                rounded_bits=self.fraction_bits,
                rounding=FixedRounding.FLOOR,
                check_underflow=False
            )
        elif isinstance(other, float):
            return other // float(self)
        elif isinstance(other, numpy.floating):
            return other // type(other)(self)
        elif isinstance(other, mpmath.mpf):
            # mpmath doesn't support //
            return mpmath.floor(other / self.mpmath())
        elif isinstance(other, mpfr_type):
            return other // self.mpfr()
        else:
            return NotImplemented

    # Modulo

    @staticmethod
    def divmod(lhs, rhs, rounding: FixedRounding, discard_div=False) -> tuple:
        """Returns the integer result of ``lhs / rhs`` and its remainder

        Args:
            lhs (Fixed, bool, int, numpy.bool, numpy.integer): Dividend
            lhs (Fixed, bool, int, numpy.bool, numpy.integer): Divisor
            rounding (FixedRounding): Rounding mode
            discard_div (bool, optional): Don't return the division result. Defaults to False.
                                          Used in cases where converting the result might overflow.

        Returns:
            Fixed, Fixed: ``round(lhs / rhs)``, ``lhs - round(lhs / rhs) * rhs``

        Note:
            At least one of ``lhs``, ``rhs`` must be :py:class:`Fixed`

        Note:
            Floating-point values aren't supported due to inaccuracies
        """

        # Letting the error occur in _div or _reverse_div will result in lhs - 0 * 0 = lhs

        if not isinstance(lhs, (Fixed, bool, int, numpy.bool, numpy.integer, mpz_type)) or  \
                not isinstance(rhs, (Fixed, bool, int, numpy.bool, numpy.integer, mpz_type)):
            return NotImplemented

        if isinstance(lhs, Fixed):
            reg = lhs._common_copy(rhs) if isinstance(rhs, Fixed) else lhs
            ret_t = fixed_alias(reg)

            if rhs == 0:
                trigger_error('undefined', 'Divide by 0')
                return ret_t() if discard_div else (ret_t(), ret_t())

            reg = reg._higher_precision()._higher_precision()  # Double increase - two operations

            if reg._div(
                rhs,
                rounded_bits=reg.fraction_bits,
                rounding=rounding,
                check_underflow=False
            ) is NotImplemented:
                return NotImplemented

            if not discard_div:
                div = ret_t(reg)  # Note: reg is modified, so it needs to be explicitly copied here

            reg *= rhs
            reg = ret_t(lhs - reg)

            return reg if discard_div else (div, reg)
        elif isinstance(rhs, Fixed):
            if rhs.value == 0:
                trigger_error('undefined', 'Divide by 0')
                return rhs._create_same() if discard_div else (rhs._create_same(), rhs._create_same())

            higher = promote(rhs)

            if isinstance(lhs, (int, mpz_type)):
                # Figure how many bits are required to represent lhs
                if lhs.bit_length() > rhs.integer_bits:
                    higher = promote(
                        Fixed(
                            fraction_bits=rhs.fraction_bits,
                            integer_bits=lhs.bit_length(),
                            sign=rhs.sign or lhs < 0
                        )
                    )
            elif isinstance(lhs, numpy.integer):
                # Similar to int
                if numpy.iinfo(lhs).bits > rhs.integer_bits:
                    higher = promote(
                        Fixed(
                            # Avoid NumPy type pollution
                            fraction_bits=rhs.fraction_bits,
                            integer_bits=int(numpy.iinfo(lhs).bits),
                            sign=bool(rhs.sign or lhs < 0)
                        )
                    )

            reg = higher(rhs)._higher_precision()

            reg = reg._reverse_div(
                lhs,
                rounded_bits=reg.fraction_bits,
                rounding=rounding,
                check_underflow=False
            )
            if reg is NotImplemented:
                return NotImplemented

            if not discard_div:
                div = rhs._create_same(reg, False)

            reg = rhs._create_same(lhs - reg * rhs, False)

            return reg if discard_div else (div, reg)
        else:
            return NotImplemented

    def __imod__(self, other) -> Self:
        """Calculates the remainder of self and a value in-place

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Divisor

        Returns:
            Fixed: self

        Note:
            Floors (like Python)
        """

        def implementation(val: int, fract: int) -> None:
            # Use Python's %, which is more accurate than
            # self - self // other * other, and requires
            # no precision increasing
            if val == 0:
                trigger_error('undefined', 'Divide by 0')
                self.value = backend_zero
            else:
                self._set(self._common_precision(val, fract, lambda a, b: a % b))

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            # Cast NumPy integers to avoid overflow
            implementation(backend(other), 0)
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                return self.__imod__(mpmath.mpmathify(other))
        elif isinstance(other, mpfr_type):
            # Match precisions
            with mpmath.workprec(mpfr_prec()):
                return self.__imod__(mpfr_to_mpf(other))
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other):
                if self.value:
                    if (self.value < 0) != (other < 0):
                        # self % -sign(self) * inf = other
                        if self.saturation:
                            self._set(other)
                        else:
                            self.value = backend_zero
                    # else x % (sign(x) * inf) = x
                # else 0 % inf = 0 % -inf = 0
            elif mpmath.isnan(other):
                trigger_error(
                    'undefined',
                    f'Undefined: operation on {self.human_format} and {other}'
                )
                self.value = backend_zero
            elif other == 0:
                trigger_error('undefined', f'Divide by 0')
                self.value = backend_zero
            elif self.value:
                # Limits:
                # By definitions, |self % other| <= |other|. When other is too small,
                # the result underflows.
                # Also, if other is a power of 2 smaller than 2 ** -fraction_bits,
                # the result will be 0, since
                # (value * 2 ** -fraction_bits) % 2 ** e =
                # (value % 2 ** e) * (2 ** -fraction_bits % 2 ** e) =
                # value % 2 ** e * 0 = 0
                #
                # This leaves the other limit: |self % other| <= 2 ** integer_bits
                # self % other = self - floor(self / other) * other, and when |self| < |other|,
                # the result is self if sign(self) = sign(other), and otherwise it's
                # self - -other * other = self + other.

                mantissa, exp, e = semi_fixed(other)

                # -1 so rounding is handled properly
                if e > self.precision + 1:
                    # other is too large
                    if (self.value < 0) != (other < 0):
                        # The result is self + other
                        self += other
                    # else self = self + 0
                elif e < -self.precision - 1:
                    if (self.value << mantissa.bit_length()) % mantissa == 0:
                        self.value = backend_zero
                    else:
                        trigger_error(
                            'underflow',
                            f'Underflow: {other} is too small for {self.human_format}.__imod__'
                        )
                        self.value = backend_zero
                        self._handle_underflow_rounding(mpmath.sign(other))
                else:
                    implementation(mantissa, exp)
            # else self = 0, 0 % other = 0

        return self

    def __mod__(self, other):
        """Divides self by a value and returns the remainder

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Divisor

        Returns:
            Result

        Note:
            Floors (like Python)
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
            return result.__imod__(other)
        elif isinstance(other, (float, numpy.floating)):
            return type(other)(self) % other
        elif isinstance(other, mpmath.mpf):
            # mpmath handles infinities differently than the other backends
            if mpmath.isinf(other):
                return other                                                        \
                    if self.value and mpmath.sign(self.value) != mpmath.sign(other) \
                    else self.mpmath()
            else:
                return self.mpmath() % other
        elif isinstance(other, mpfr_type):
            return self.mpfr() % other
        else:
            return NotImplemented

    def __rmod__(self, other):
        """Divides a value by self and returns the remainder

        Args:
            other (bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Dividend

        Returns:
            Result

        Note:
            Floors (like Python)
        """

        if isinstance(other, Fixed):
            return NotImplemented

        if isinstance(other, (bool, int, numpy.bool, numpy.bool, numpy.integer, mpz_type)):
            return Fixed.divmod(other, self, FixedRounding.FLOOR, discard_div=True)
        elif isinstance(other, (float, numpy.floating)):
            return other % type(other)(self)
        elif isinstance(other, mpmath.mpf):
            return other % self.mpmath()
        elif isinstance(other, mpfr_type):
            return other % self.mpfr()
        else:
            return NotImplemented

    # divmod

    def __divmod__(self, other) -> tuple:
        """Efficiently divides self by a value and returns the result and the remainder

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Divisor

        Returns:
            tuple: Result, Remainder

        Note:
            Floors (like Python)
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            return Fixed.divmod(self, other, FixedRounding.FLOOR)
        elif isinstance(other, (float, numpy.floating)):
            return divmod(type(other)(self), other)
        elif isinstance(other, mpmath.mpf):
            return self // other, self % other
        elif isinstance(other, mpfr_type):
            return divmod(self.mpfr(), other)
        else:
            return NotImplemented

    def __rdivmod__(self, other) -> tuple:
        """Efficiently divides a value by self and returns the result and the remainder

        Args:
            other (bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Dividend

        Returns:
            tuple: Result, Remainder

        Note:
            Floors (like Python)
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            return Fixed.divmod(other, self, FixedRounding.FLOOR)
        elif isinstance(other, (float, numpy.floating)):
            return divmod(other, type(other)(self))
        elif isinstance(other, mpmath.mpf):
            return other // self, other % self
        elif isinstance(other, mpfr_type):
            return divmod(other, self.mpfr())
        else:
            return NotImplemented

    # Shifts (multiply/divide by a power of 2)

    def __ilshift__(self, other) -> Self:
        """Left shift self in-place, i.e. multiply by 2 ** other

        Args:
            other (bool, int, numpy.bool, numpy.integer): Bit count to shift by. May be negative.

        Returns:
            Fixed: self
        """

        if not isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            return NotImplemented

        return self.__irshift__(-backend(other))

    def __lshift__(self, other) -> Self:
        """Left shift self, i.e. multiply by 2 ** other

        Args:
            other (bool, int, numpy.bool, numpy.integer): Bit count to shift by. May be negative.

        Returns:
            Fixed: Result
        """

        result = self._create_copy()
        return result.__ilshift__(other)

    def __irshift__(self, other) -> Self:
        """Right shift self in-place, i.e. divide by 2 ** other

        Args:
            other (bool, int, numpy.bool, numpy.integer): Bit count to shift by. May be negative.

        Returns:
            Fixed: self
        """

        if not isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            return NotImplemented

        # Limit other because integer shifting takes a long time for large values
        limit = 4 * self.bits

        self._set(
            shift_round(
                self.value,
                backend(min(max(other, -limit), limit))
            )
        )
        return self

    def __rshift__(self, other) -> Self:
        """Right shift self, i.e. divide by 2 ** other

        Args:
            other (bool, int, numpy.bool, numpy.integer): Bit count to shift by. May be negative.

        Returns:
            Fixed: Result
        """

        result = self._create_copy()
        return result.__irshift__(other)

    # Bitwise

    def __iand__(self, other) -> Self:
        """In-place bitwise ANDs self and a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer): Value to AND with

        Returns:
            Fixed: self
        """

        def implementation(val: int, fract: int):
            self._set(
                self._common_precision(
                    val,
                    fract,
                    lambda a, b: a & b
                )
            )

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            implementation(backend(other), 0)
        else:
            return NotImplemented

        return self

    def __and__(self, other) -> Self:
        """Bitwise ANDs self and a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer): Value to AND with

        Returns:
            Fixed: Result
        """

        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__iand__(other)

    def __rand__(self, other) -> Self:
        """Bitwise ANDs a value and self

        Args:
            other (bool, int, numpy.bool, numpy.integer): Value to AND with

        Returns:
            Fixed: Result
        """

        if isinstance(other, Fixed):
            return NotImplemented

        return self & other

    def __ior__(self, other) -> Self:
        """In-place bitwise ORs self and a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer): Value to OR with

        Returns:
            Fixed: self
        """

        def implementation(val: int, fract: int):
            self._set(
                self._common_precision(
                    val,
                    fract,
                    lambda a, b: a | b
                )
            )

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            implementation(backend(other), 0)
        else:
            return NotImplemented

        return self

    def __or__(self, other) -> Self:
        """Bitwise ORs self and a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer): Value to OR with

        Returns:
            Fixed: Result
        """

        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__ior__(other)

    def __ror__(self, other) -> Self:
        """Bitwise ORs a value and self

        Args:
            other (bool, int, numpy.bool, numpy.integer): Value to OR with

        Returns:
            Fixed: Result
        """

        if isinstance(other, Fixed):
            return NotImplemented

        return self | other

    def __ixor__(self, other) -> Self:
        """In-place bitwise XORs self and a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer): Value to XOR with

        Returns:
            Fixed: self
        """

        def implementation(val: int, fract: int):
            self._set(
                self._common_precision(
                    val,
                    fract,
                    lambda a, b: a ^ b
                )
            )

        if isinstance(other, Fixed):
            implementation(other.value, other.fraction_bits)
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            implementation(backend(other), 0)
        else:
            return NotImplemented

        return self

    def __xor__(self, other) -> Self:
        """Bitwise XORs self and a value

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer): Value to XOR with

        Returns:
            Fixed: Result
        """

        result = self._common_copy(other) if isinstance(other, Fixed) else self._create_copy()
        return result.__ixor__(other)

    def __rxor__(self, other) -> Self:
        """Bitwise XORs a value and self

        Args:
            other (bool, int, numpy.bool, numpy.integer): Value to XOR with

        Returns:
            Fixed: Result
        """

        if isinstance(other, Fixed):
            return NotImplemented

        return self ^ other

    # Comparisons

    def cmp(self, other) -> int | float:
        """Compares Fixed and another value via subtraction

        Args:
            other (Fixed, bool, int, numpy.bool, numpy.integer, float, numpy.floating, mpmath.mpf):
                Value to compare against

        Returns:
            int, float:
                Comparison result.          \f
                Positive means self > other.\f
                0 means self == other.      \f
                Negative means self < other.\f
                NaN means other is Nan.
        """

        if isinstance(other, Fixed):
            return self._common_precision(other.value, other.fraction_bits, lambda a, b: a - b, False)
        elif isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type)):
            return self.value - (backend(other) << self.fraction_bits)
        elif isinstance(other, (float, numpy.floating)):
            # Convert to mpmath
            with mpmath.workprec(numpy.finfo(other).nmant + 1):
                return self.cmp(mpmath.mpmathify(other))
        elif isinstance(other, mpfr_type):
            # Match precision
            with mpmath.workprec(mpfr_prec()):
                return self.cmp(mpfr_to_mpf(other))
        elif isinstance(other, mpmath.mpf):
            if mpmath.isinf(other):
                return -backend(mpmath.sign(other))
            elif mpmath.isnan(other):
                return math.nan

            if other == 0:
                return self.value

            mantissa, exp, e = semi_fixed(other)

            if e >= self.sign + self.integer_bits:
                # other is outside self's range
                return -backend(mpmath.sign(other))
            elif e >= -self.fraction_bits:
                # Treat it like a fixed
                return self._common_precision(mantissa, exp, lambda a, b: a - b, False)
            else:
                # Other is smaller than self.epsilon.
                # If self < 0, then other > self.
                # If self > 0, then other < self.
                # If self = 0, then compare other with 0.
                return self.value if self.value else -backend(mpmath.sign(other))
        else:
            return NotImplemented

    def __eq__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result == 0

    def __ne__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result != 0

    def __lt__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result < 0

    def __le__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result <= 0

    def __gt__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result > 0

    def __ge__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result >= 0

    # NumPy support (avoid conversions to numpy.floating)

    def __array_ufunc__(self, ufunc, method, *args, **kwargs):
        """Internal function for NumPy.\f
           Avoids NumPy converting Fixed to numpy.double.
        """

        cmp_ops = {
            numpy.equal: ('__eq__', lambda diff: diff == 0),
            numpy.not_equal: ('__ne__', lambda diff: diff != 0),
            numpy.less: ('__lt__', lambda diff: diff > 0),
            numpy.less_equal: ('__le__', lambda diff: diff >= 0),
            numpy.greater: ('__gt__', lambda diff: diff < 0),
            numpy.greater_equal: ('__ge__', lambda diff: diff <= 0),
        }

        ops = {
            numpy.add: 'add__',
            numpy.subtract: 'sub__',
            numpy.multiply: 'mul__',
            numpy.divide: 'truediv__',
            numpy.floor_divide: 'floordiv__',
            numpy.mod: 'mod__',
            numpy.divmod: 'divmod__',
            numpy.left_shift: 'lshift__',
            numpy.right_shift: 'rshift__',
            numpy.bitwise_and: 'and__',
            numpy.bitwise_or: 'or__',
            numpy.bitwise_xor: 'xor__',
            numpy.abs: 'abs__',
        }

        if method == '__call__':
            if ufunc in ops:
                name = ops[ufunc]

                if isinstance(args[0], Fixed):
                    return getattr(Fixed, '__' + name)(*args)
                elif not 'shift' in name:
                    return getattr(Fixed, '__r' + name)(*(args[::-1]))
            elif ufunc in cmp_ops:
                if isinstance(args[0], Fixed):
                    return getattr(Fixed, cmp_ops[ufunc][0])(*args)
                else:
                    if args[0].size == 1:
                        return cmp_ops[ufunc][1](args[1].cmp(args[0].dtype.type(args[0])))
                    # else return NotImplemented
            elif ufunc == numpy.sign:
                return sign(self)

        return NotImplemented

# Aliases


class FixedAlias(FixedConfig):
    """Provides a type alias for pre-configured fixed-point
    """

    def __init__(self, fraction_bits: int, integer_bits: int, sign: bool, saturation: bool):
        """Creates a new alias

        Args:
            fraction_bits (int): Fraction bits
            integer_bits (int): Integer bits
            sign (bool): Signedness
            saturation (bool): Saturation
        """

        # Let Fixed handle the invalid configurations
        self.properties = Fixed(
            fraction_bits=fraction_bits,
            integer_bits=integer_bits,
            sign=sign,
            saturation=saturation
        ).properties

    def __call__(self, *args, **kwargs) -> Fixed:
        """Creates a new fixed-point variable

        Returns:
            Fixed: Variable
        """

        return Fixed(
            *args,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign,
            saturation=self.saturation,
            **kwargs
        )


@functools.cache
def create_alias(f: int, i: int, s: bool, sat: bool) -> FixedAlias:
    """Creates a fixed-point alias

    Args:
        f (int): Fraction bits
        i (int): Integer bits
        s (bool): Signedness
        sat (bool): Saturation

    Returns:
        FixedAlias: Alias
    """

    return FixedAlias(f, i, s, sat)


q7 = create_alias(7, 0, True, True)
"""Alias of Q7/Q1.7/Fixed<7, 0, signed, saturated>
"""

q15 = create_alias(15, 0, True, True)
"""Alias of Q15/Q1.15/Fixed<15, 0, signed, saturated>
"""

q31 = create_alias(31, 0, True, True)
"""Alias of Q31/Q1.31/Fixed<31, 0, signed, saturated>
"""

q9_7 = create_alias(7, 8, True, True)
"""Alias of Q9.7/Fixed<7, 8, signed, saturated>
"""

q17_15 = create_alias(15, 16, True, True)
"""Alias of Q17.15/Fixed<15, 16, signed, saturated>
"""

q33_31 = create_alias(31, 32, True, True)
"""Alias of Q33.31/Fixed<31, 32, signed, saturated>
"""


def fixed_alias(value: Fixed) -> FixedAlias:
    """Create a type alias from a fixed-point value

    Args:
        value (Fixed): Value to create an alias of

    Returns:
        FixedAlias: Fixed-point alias
    """

    if not isinstance(value, Fixed):
        raise TypeError('Invalid type')

    return create_alias(value.fraction_bits, value.integer_bits, value.sign, value.saturation)


def promote_sum(value: type | Fixed) -> type:
    """Promotes a fixed type to higher precision for multiple summations

    Args:
        value (type, Fixed): Fixed type, or value to extract the type of

    Returns:
        type: Promoted type
    """

    if isinstance(value, type):
        value = value()

    if not isinstance(value, Fixed):
        raise TypeError('Invalid type')

    return create_alias(
        value.fraction_bits,
        2 * value.integer_bits + value.fraction_bits + value.sign,
        True,
        value.saturation
    )


def promote_prod(value: type | Fixed) -> type:
    """Promotes a fixed type to higher precision for product operations (e.g. convolution)

    Args:
        value (type, Fixed): Fixed type, or value to extract the type of

    Returns:
        type: Promoted type
    """

    if isinstance(value, type):
        value = value()

    if not isinstance(value, Fixed):
        raise TypeError('Invalid type')

    # Promote for summation and multiply everything by 2
    return create_alias(
        2 * value.fraction_bits,
        2 * (2 * value.integer_bits + value.fraction_bits + value.sign) + 1,
        True,
        value.saturation
    )


def promote(value: type | Fixed) -> type:
    """Promotes a fixed type to higher precision

    Args:
        value (type, Fixed): Fixed type, or value to extract the type of

    Returns:
        type: Promoted type

    Note:
        The returned type is suitable for all operations, assuming only 1 operation is performed.
        It guarantees that there will be no over/underflow when operating on the original precision.
    """

    if isinstance(value, type):
        value = value()

    if not isinstance(value, Fixed):
        raise TypeError('Invalid type')

    return create_alias(
        2 * (value.fraction_bits + value.integer_bits + value.sign),
        2 * (value.fraction_bits + value.integer_bits + value.sign),
        True,
        value.saturation
    )


def frexp(x: Fixed) -> tuple:
    """Decomposes x to fraction and exponent

    Args:
        x (Fixed): Number to decompose

    Returns:
        tuple:
            ``fraction``: Fixed-point number with a magnitude in the
            range [0.5, 1) or 0, and with the same precision as x.\f
            ``exponent``: Integer exponent.\f
            ``fraction * 2 ** exponent = x``
    """

    # x is currently a.b * 2 ** -fraction_bits
    # We want to convert it to 0.f * 2 ** e.
    # We get 0.f by shifting the internal value left such that the MSB is at the highest possible
    # position, and then calculate the exponent as bits shifted - fraction bits.

    # value * 2 ** -fraction_bits = f * 2 ** e
    # f = norm(value) = value / 2 ** ceil(log2(value))
    # ceil(log2(value)) = value.bit_length
    # f = value >> value.bit_length
    #
    # 2 ** e = value / f * 2 ** -fraction_bits
    # = value / (value / 2 ** value.bit_length * 2 ** -fraction_bits
    # = 2 ** value.bit_length * 2 ** -fraction_bits
    # e = value.bit_length - fraction_bits

    if not isinstance(x, Fixed):
        raise TypeError('Invalid type')

    bits = x.fraction_bits + x.integer_bits

    if bits == 0:
        # Edge case of Fixed<0, 0, True>, which can't represent 0.5
        return x, 0

    if x.value == 0:
        return Fixed(
            0,
            fraction_bits=bits,
            integer_bits=0,
            sign=x.sign,
            saturation=x.saturation
        ), 0

    bit_length = x.value.bit_length()
    scale = bits - bit_length  # bits - bit_length because we also change format

    return Fixed(
        (x.value << scale) if scale >= 0 else (x.value >> -scale),
        fraction_bits=bits,
        integer_bits=0,
        sign=x.sign,
        saturation=x.saturation,
        internal=True
    ), bit_length - x.fraction_bits


def modf(x: Fixed) -> tuple:
    """Similar to C's modf, splits x to integer and fraction components

    Args:
        x (Fixed): Number to splits

    Returns:
        tuple: fraction, integer
    """

    x_t = fixed_alias(x)

    return sign(x) * x_t(abs(x.value) & (x.one - 1), internal=True), x_t(
        prepare_round(x.value, x.fraction_bits, rounding=FixedRounding.TRUNC) & -x.one,
        internal=True
    )


def sign(x: Fixed) -> int:
    """Returns the sign of x, or 0 if ``x == 0``

    Args:
        x (Fixed): Input

    Returns:
        int: -1, 0 or 1
    """

    if not isinstance(x, Fixed):
        raise TypeError('Invalid type')

    if x.value > 0:
        return 1
    elif x.value < 0:
        return -1
    else:
        return 0


def copysign(
    mag: bool | int | float | numpy.bool | numpy.integer | numpy.floating | mpmath.mpf | Fixed,
    sgn: bool | int | float | numpy.bool | numpy.integer | numpy.floating | mpmath.mpf | Fixed
):
    """Similar to C's copysign, applies sgn's sign to mag's magnitude

    Args:
        mag: Magnitude
        sgn: Sign

    Returns:
        type(mag): ``-abs(mag) if sgn < 0 else abs(mag)``

    Note:
        ``-0.0`` is considered negative
    """

    if not isinstance(mag, Fixed) and not isinstance(sgn, Fixed):
        raise TypeError('Invalid types')

    if isinstance(mag, numpy.bool):
        mag = bool(mag)

    # Handle -0 and NaN
    if isinstance(mag, (float, numpy.floating)):
        mag_sign = numpy.signbit(mag)
    elif isinstance(mag, mpmath.mpf):
        mag_sign = bool(mag._mpf_[0])
    elif isinstance(mag, mpfr_type):
        mag_sign = mag.is_signed()
    else:
        mag_sign = mag < 0

    if isinstance(sgn, (float, numpy.floating)):
        sgn_sign = numpy.signbit(sgn)
    elif isinstance(sgn, mpmath.mpf):
        sgn_sign = bool(sgn._mpf_[0])
    elif isinstance(sgn, mpfr_type):
        sgn_sign = sgn.is_signed()
    else:
        sgn_sign = sgn < 0

    return mag if mag_sign == sgn_sign else -mag


def nextafter(
    _from: bool | int | float | numpy.bool | numpy.integer | numpy.floating | mpmath.mpf | Fixed,
    to: bool | int | float | numpy.bool | numpy.integer | numpy.floating | mpmath.mpf | Fixed
):
    """Similar to C's nextafter, returns the value after ``_from`` in the direction of ``to``

    Args:
        _from: Value to start from
        to: Value to go towards

    Returns:
        type(_from): Next value that's closer to ``to``

    Note:
        Overflow might occur
    """

    if not isinstance(_from, Fixed) and not isinstance(to, Fixed):
        raise TypeError('Invalid types')

    from_t = fixed_alias(_from) if isinstance(_from, Fixed) else type(_from)

    if float_is_nan(_from) or float_is_nan(to):
        return from_t(math.nan)

    if isinstance(_from, Fixed):
        cmp = _from.cmp(to)
    else:
        cmp = -to.cmp(_from)

    if cmp == 0:
        return _from
    else:
        s = -1 if cmp > 0 else 1  # Reversed because we go towards to
        if isinstance(_from, (bool, numpy.bool)):
            return not _from
        elif isinstance(_from, (int, mpz_type)):
            return from_t(_from + s)
        elif isinstance(_from, numpy.integer):
            if numpy.iinfo(_from).kind == 'u':
                return _from + from_t(1) if s > 0 else _from - from_t(1)
            else:
                return _from + from_t(s)
        elif isinstance(_from, (float, numpy.floating)):
            return numpy.nextafter(_from, s * numpy.inf)
        elif isinstance(_from, mpmath.mpf):
            if mpmath.isinf(_from):
                # Note: normally nextafter can return the finite values
                # before/after infinities, but mpmath is unlimited
                return _from
            else:
                f, e = mpmath.frexp(_from)
                f += s * mpmath.eps / 2
                return mpmath.ldexp(f, e)
        elif isinstance(_from, mpfr_type):
            return gmpy2.next_toward(_from, gmpy2.inf(s))
        elif isinstance(_from, Fixed):
            if _from.fraction_bits == 0:
                return _from + s
            elif _from.sign:
                eps = from_t(s, internal=True)
                return _from + eps
            else:
                eps = from_t(1, internal=True)
                return _from + eps if s == 1 else _from - eps
        else:
            raise TypeError('Invalid type')


def ilogb(x: Fixed) -> int:
    """Similar to C's ilogb, returns a number ``n`` such that ``1 <= abs(x) / 2 ** n < 2``

    Args:
        x (Fixed): Input

    Raises:
        FixedUndefined: ``x`` is 0

    Returns:
        int: ``floor(log2(x))``
    """

    if x:
        return x.value.bit_length() - 1 - x.fraction_bits
    else:
        trigger_error('undefined', 'ilogb(0) is undefined')
        return math.nan
