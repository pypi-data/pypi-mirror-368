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

"""Internal complex fixed-point implementation module
"""

from pyfixed.fixed import *
from typing import overload


class PartialOrdering(enum.Enum):
    """Partial ordering enum, similar to C++'s:
       https://en.cppreference.com/w/cpp/utility/compare/partial_ordering
    """

    LESS = enum.auto()
    """LHS is less than RHS
    """

    EQUAL = enum.auto()
    """LHS is equal to RHS
    """

    GREATER = enum.auto()
    """LHS is greater than RHS
    """

    UNORDERED = enum.auto()
    """LHS and RHS can't be ordered relative to each other
    """


class ComplexFixed(FixedConfig):
    """Complex fixed-point

    Attributes:
        real (Fixed): Real component
        imag (Fixed): Imaginary component
    """

    @property
    def properties(self) -> FixedProperties:
        """Class' fixed-point properties
        """

        return self.real.properties

    @property
    def human_format(self) -> str:
        """A human-readable fixed-point string representing this class
        """

        return 'Complex' + self.real.human_format

    def _create_same(self, *args, **kwargs) -> Self:
        """Creates a complex fixed-point number of the same configuration as self

        Args:
            Same as ComplexFixed.__init__

        Returns:
            ComplexFixed: New complex fixed-point number
        """

        return ComplexFixed(
            *args,
            **kwargs,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign,
            saturation=self.saturation
        )

    def _create_copy(self) -> Self:
        """Creates a copy of this number

        Returns:
            ComplexFixed: Copy
        """

        return self._create_same(self)

    def _create_common(self, other: Fixed | Self, *args, **kwargs) -> Self:
        """Creates a number in a common precision

        Args:
            other (Fixed, ComplexFixed): Other fixed
            ...: Arguments for ComplexFixed.__init__

        Returns:
            ComplexFixed: Common precision number
        """

        return ComplexFixed(
            *args,
            **kwargs,
            fraction_bits=max(self.fraction_bits, other.fraction_bits),
            integer_bits=max(self.integer_bits, other.integer_bits),
            sign=self.sign or other.sign,
            saturation=self.saturation or other.saturation

        )

    def _common_copy(self, other: Fixed | Self) -> Self:
        """Creates a copy of self in a common precision

        Args:
            other (Fixed, ComplexFixed): Other fixed

        Returns:
            ComplexFixed: Common precision copy
        """

        return self._create_common(other, self)

    def _higher_precision(self) -> Self:
        """Creates a higher precision copy of this number

        Returns:
            ComplexFixed: Higher precision copy
        """

        r = promote(self.real)()

        return ComplexFixed(
            self,
            fraction_bits=r.fraction_bits,
            integer_bits=r.integer_bits,
            sign=True,
            saturation=self.saturation
        )

    @staticmethod
    def _is_real_type(x) -> bool:
        """Checks if x's type is real

        Args:
            x (any): Number to check the type of

        Returns:
            bool: Whether x is real
        """

        return isinstance(
            x,
            (
                bool,
                int,
                float,
                numpy.bool,
                numpy.integer,
                numpy.floating,
                mpmath.mpf,
                mpz_type,
                mpfr_type,
                Fixed,
            )
        )

    @staticmethod
    def _is_complex_type(x) -> bool:
        """Checks if x's type is complex

        Args:
            x (any): Number to check the type of

        Returns:
            bool: Whether x is complex
        """

        return isinstance(
            x,
            (
                complex,
                numpy.complexfloating,
                mpmath.mpc,
                mpc_type,
                ComplexFixed,
            )
        )

    def _isnan(self, x) -> bool:
        """Checks if x is NaN and triggers an error if so

        Args:
            x (any): Number to check

        Returns:
            bool: x != x
        """

        if x != x:
            trigger_error(
                'undefined',
                f'Undefined: operation on {self.human_format} and {x}'
            )
            return True
        else:
            return False

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
            ComplexFixed: result (self or NotImplemented)
        """

        if ComplexFixed._is_real_type(other):
            self.real._div(other, rounded_bits, rounding, check_underflow)
            self.imag._div(other, rounded_bits, rounding, check_underflow)
        elif isinstance(other, ComplexFixed):
            # (a + bi) / (c + di) = (a + bi)(c - di) / (c ** 2 + d ** 2)
            # Precision is increased to avoid over/underflow

            a = self.real._higher_precision()._higher_precision()
            b = self.imag._higher_precision()._higher_precision()
            c = other.real._higher_precision()._higher_precision()
            d = other.imag._higher_precision()._higher_precision()

            mul_r = a * c + b * d
            mul_i = b * c - a * d

            if rounded_bits:
                rounded_bits += mul_r.fraction_bits - self.fraction_bits

            c_d = c * c + d * d
            self.real._set(
                shift_round(
                    mul_r._div(
                        c_d,
                        rounded_bits,
                        rounding,
                        check_underflow
                    ).value,
                    mul_r.fraction_bits - self.fraction_bits,
                    rounding,
                    check_underflow
                )
            )
            self.imag._set(
                shift_round(
                    mul_i._div(
                        c_d,
                        rounded_bits,
                        rounding,
                        check_underflow
                    ).value,
                    mul_i.fraction_bits - self.fraction_bits,
                    rounding,
                    check_underflow
                )
            )
        elif ComplexFixed._is_complex_type(other):
            trigger_error(
                'undefined',
                "In-place operations involving complex floats aren't supported"
            )
        else:
            return NotImplemented

        return self

    def _reverse_div(
        self,
        other,
        rounded_bits: int = None,
        rounding: FixedRounding = None,
        check_underflow: bool = True
    ) -> Self:
        """Divides a number by self

        Args:
            other (any): Dividend
            rounded_bits (int, optional): Bits to round, starting from LSB.
                                          Defaults to None (normal rounding).
            rounding (FixedRounding, optional): Rounding mode. Defaults to current state's.
            check_underflow (bool, optional): Check for underflow. Defaults to True.

        Returns:
            ComplexFixed: result (or NotImplemented)
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            # a / (c + di) = a * (c - di) / (c ** 2 + d ** 2)

            c = self.real._higher_precision()._higher_precision()
            d = self.imag._higher_precision()._higher_precision()
            c_d = c * c + d * d

            if not self.saturation and isinstance(other, (int, numpy.integer, mpz_type)):
                other_fixed = Fixed(
                    other,
                    fraction_bits=0,
                    integer_bits=2 * numpy.iinfo(other).bits
                    if isinstance(other, numpy.integer) else
                    2 * (other.bit_length() + 1),
                    sign=True,
                    saturation=True
                )
                mul_r = c * other_fixed
                mul_i = -d * other_fixed
            else:
                mul_r = c * other
                mul_i = -d * other

            if rounded_bits is not None:
                rounded_bits += mul_r.fraction_bits - self.fraction_bits
            else:
                rounded_bits = 0

            result = self._create_common(other)\
                if isinstance(other, Fixed)    \
                else self._create_same()

            result.real._set(
                shift_round(
                    mul_r._div(c_d, rounded_bits, rounding, check_underflow).value,
                    mul_r.fraction_bits - result.fraction_bits,
                    rounding,
                    check_underflow
                )
            )
            result.imag._set(
                shift_round(
                    mul_i._div(c_d, rounded_bits, rounding, check_underflow).value,
                    mul_i.fraction_bits - result.fraction_bits,
                    rounding,
                    check_underflow
                )
            )

            return result
        else:
            return NotImplemented

    @staticmethod
    def _floordiv_helper(a, b):
        """Helper function for floor division

        Args:
            a (any): Dividend
            b (any): Divisor

        Returns:
            Floored division result
        """

        # Divide and floor, avoid flooring NaN (some types don't like it)
        div = a / b

        if isinstance(div, (numpy.floating, numpy.complexfloating)):
            return numpy.floor(div.real) + 1j * numpy.floor(div.imag)
        elif isinstance(div, (float, complex)):
            return complex(
                math.floor(div.real) if math.isfinite(div.real) else div.real,
                math.floor(div.imag) if math.isfinite(div.imag) else div.imag,
            )
        elif isinstance(div, (mpmath.mpf, mpmath.mpc)):
            return mpmath.floor(div)
        elif isinstance(div, (mpfr_type, mpc_type)):
            return gmpy2.mpc(
                gmpy2.floor(div.real) if gmpy2.is_finite(div.real) else div.real,
                gmpy2.floor(div.imag) if gmpy2.is_finite(div.imag) else div.imag
            )
        else:
            return NotImplemented

    @staticmethod
    def _complex_type_helper(other) -> type:
        """Returns the complex type of a number

        Args:
            other (any): Number

        Returns:
            type: Complex type
        """

        return type(other + 0j)

    @overload
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
            Fixed |
            Self
        = None,
        fraction_bits: int = None,
        integer_bits: int = None,
        sign: bool = None,
        saturation: bool = None,
        internal=False,
    ): ...

    @overload
    def __init__(
        self,
        real:
            bool |
            int |
            float |
            numpy.bool |
            numpy.integer |
            numpy.floating |
            mpmath.mpf |
            Fixed
        = None,
        imag:
            bool |
            int |
            float |
            numpy.bool |
            numpy.integer |
            numpy.floating |
            mpmath.mpf |
            Fixed
        = None,
        fraction_bits: int = None,
        integer_bits: int = None,
        sign: bool = None,
        saturation: bool = None,
        internal=False,
    ): ...

    def __init__(
        self,
        a:
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
            Fixed |
            Self
        = None,
        b:
            bool |
            int |
            float |
            numpy.bool |
            numpy.integer |
            numpy.floating |
            mpmath.mpf |
            Fixed
        = None,
        fraction_bits: int = None,
        integer_bits: int = None,
        sign: bool = None,
        saturation: bool = None,
        internal=False,
    ):
        """Initializes a new fixed-point complex number

        Args:
            value: Initial value. Defaults to None. Mutually exclusive with 'real' and 'imag'.
            real: Initial real value. Defaults to None. Mutually exclusive with 'value'.
            imag: Initial imaginary value. Defaults to None. Mutually exclusive with 'value'.
            fraction_bits (int, optional): Number of fraction bits. Defaults to 52.
            integer_bits (int, optional): Number of integer bits. Defaults to 11.
            sign (bool, optional): Signedness. Defaults to True.
            saturation (bool, optional): Saturation. Defaults to True.
            internal (bool, optional): Directly store the initial value(s). Defaults to False.

        Raises:
            TypeError: value isn't a real/complex number
            TypeError: real and/or imag are not real numbers (or None)
        """

        if b is None:
            value = a
            real = None
            imag = None
        else:
            value = None
            real = a
            imag = b

        if ComplexFixed._is_complex_type(real) or ComplexFixed._is_complex_type(imag):
            raise TypeError("'real' and 'imag' must be of real types")

        # Deduce configuration
        if isinstance(value, (Fixed, ComplexFixed)):
            if fraction_bits is None:
                fraction_bits = value.fraction_bits
            if integer_bits is None:
                integer_bits = value.integer_bits
            if sign is None:
                sign = value.sign
            if saturation is None:
                saturation = value.saturation
        elif isinstance(real, Fixed) or isinstance(imag, Fixed):
            r_fixed = real if isinstance(real, Fixed) else imag
            i_fixed = imag if isinstance(imag, Fixed) else real

            if fraction_bits is None:
                fraction_bits = max(r_fixed.fraction_bits, i_fixed.fraction_bits)
            if integer_bits is None:
                integer_bits = max(r_fixed.integer_bits, i_fixed.integer_bits)
            if sign is None:
                sign = r_fixed.sign or i_fixed.sign
            if saturation is None:
                saturation = r_fixed.saturation or i_fixed.saturation
        else:
            if fraction_bits is None:
                fraction_bits = 52
            if integer_bits is None:
                integer_bits = 11
            if sign is None:
                sign = True
            if saturation is None:
                saturation = True

        fixed_type = create_alias(fraction_bits, integer_bits, sign, saturation)

        if value is not None:
            if ComplexFixed._is_real_type(value):
                init_real = value
                init_imag = 0
            elif ComplexFixed._is_complex_type(value):
                init_real = value.real
                init_imag = value.imag
            else:
                raise TypeError(f'Unrecognized type {type(value)}')
        else:
            init_real = real if real is not None else 0
            init_imag = imag if imag is not None else 0

        self.real = fixed_type(init_real, internal=internal)
        self.imag = fixed_type(init_imag, internal=internal)

    # Conversions

    def __bool__(self) -> bool:
        """Converts to boolean

        Returns:
            bool: self != 0
        """

        return bool(self.real) or bool(self.imag)

    def __int__(self) -> int:
        """Converts the real component to a Python integer, discarding the imaginary component

        Returns:
            int: int(self.real)

        Note:
            Ignores underflow
        """

        return int(self.real)

    def __float__(self) -> float:
        """Converts the real component to a Python float, discarding the imaginary component

        Returns:
            float: float(self.real)

        Note:
            Ignores underflow
        """

        return float(self.real)

    def __complex__(self) -> complex:
        """Converts to a Python complex

        Returns:
            complex: complex(self)

        Note:
            Ignores underflow
        """

        return complex(float(self.real), float(self.imag))

    def __repr__(self) -> str:
        """Converts to a representation string

        Returns:
            str: Human format + value string
        """

        return f'{self.human_format}({str(self)})'

    def __str__(self) -> str:
        """Converts to a string

        Returns:
            str: self.real +- 1j * self.imag
        """

        imag_sign = self.imag.value < 0
        return f'{str(self.real)} {"-" if imag_sign else "+"} 1j * {str(self.imag)[imag_sign:]}'

    def __format__(self) -> str:
        """Converts to a string for formatting

        Returns:
            str: str(self)
        """

        return str(self)

    def __bytes__(self) -> bytes:
        """Converts to a byte string, which can be used directly in C

        Returns:
            bytes: bytes(self.real) + bytes(self.imag)
        """

        return bytes(self.real) + bytes(self.imag)

    def __array__(self, dtype_meta=numpy.dtypes.Complex128DType, copy: bool = True) -> numpy.ndarray:
        """Converts to NumPy

        Args:
            dtype_meta (numpy._DTypeMeta, optional): dtype meta from NumPy.
                                                     Defaults to complex double.
            copy (bool, optional) Create a copy.
                                  Defaults to True.

        Raises:
            TypeError: copy=False

        Returns:
            numpy.ndarray: Converted value
        """

        dtype = dtype_meta.type

        if copy is False:
            raise TypeError(f'Casting ComplexFixed to {dtype} requires creating a copy')

        if issubclass(dtype, numpy.complexfloating):
            return numpy.array(dtype(self.real) + 1j * dtype(self.imag))
        elif issubclass(dtype, numpy.bool):
            return numpy.array(numpy.bool(self.real) or numpy.bool(self.imag))
        else:
            warnings.warn(
                numpy.exceptions.ComplexWarning(
                    'Casting complex values to real discards the imaginary component'
                ),
                stacklevel=2
            )
            return numpy.array(dtype(self.real))

    def mpmath(self) -> mpmath.mpc:
        """Converts to mpmath.mpc

        Returns:
            mpmath.mpc: Converted value

        Note:
            The _mpc_ property can't be used because it makes mpmath think the class is mpmath.mpc
        """

        return mpmath.mpc(self.real.mpmath(), self.imag.mpmath())

    def mpz(self):
        """Converts to gmpy2.mpz

        Returns:
            gmpy2.mpz: gmpy2.mpz(self.real)

        Note:
            Ignores underflow
        """

        return self.real.mpz()

    def mpfr(self):
        """Converts to gmpy2.mpfr

        Returns:
            gmpy2.mpfr: gmpy2.mpfr(self.real)
        """

        return self.real.mpfr()

    def mpc(self):
        """Converts to gmpy2.mpc

        Returns:
            gmpy2.mpc: Converted value
        """

        if mpc_type is complex:
            raise ModuleNotFoundError('No module named gmpy2')

        return gmpy2.mpc(self.real.mpfr(), self.imag.mpfr())

    # Unary operators

    def __pos__(self) -> Self:
        """Creates a copy of self

        Returns:
            ComplexFixed: Copy of self
        """

        return self._create_copy()

    def __neg__(self) -> Self:
        """Negates self

        Returns:
            ComplexFixed: -self
        """

        return self._create_same(-self.real, -self.imag)

    # Rounding

    def __floor__(self) -> tuple:
        """Rounds both components towards -inf

        Returns:
            tuple:
                Complex integer number (casting to Python's complex
                will cast to float, potentially causing inaccuracies)

        Note:
            Ignores underflow
        """

        return self.real.__floor__(), self.imag.__floor__()

    def __ceil__(self) -> tuple:
        """Rounds both components towards +inf

        Returns:
            tuple:
                Complex integer number (casting to Python's complex
                will cast to float, potentially causing inaccuracies)

        Note:
            Ignores underflow
        """

        return self.real.__ceil__(), self.imag.__ceil__()

    def __trunc__(self) -> tuple:
        """Rounds both components towards 0

        Returns:
            tuple:
                Complex integer number (casting to Python's complex
                will cast to float, potentially causing inaccuracies)

        Note:
            Ignores underflow
        """

        return self.real.__trunc__(), self.imag.__trunc__()

    def __round__(self, ndigits: int = None) -> tuple | Self:
        """Rounds both components

        Args:
            ndigits (int, optional): Round up to 'ndigits' digits after the point.
                                     Unlike conventional 'round', digits are binary.
                                     Defaults to None.

        Raises:
            FixedOverflow: When ndigits is not None and the result is outside the class' range

        Returns:
            tuple, ComplexFixed:
            Complex integer number when ndigits is None (see __floor__).\f
            Rounded fixed-point values when ndigits is an integer.

        Note:
            Ignores underflow
        """

        if ndigits is None:
            return round(self.real), round(self.imag)

        return self._create_same(round(self.real, ndigits), round(self.imag, ndigits))

    # Binary operators

    # Addition

    def __iadd__(self, other) -> Self:
        """Adds a value to self in-place

        Args:
            other: Value to add

        Raises:
            FixedUndefined: If other is complex floating (consistency with other operators)

        Returns:
            ComplexFixed: self
        """

        if ComplexFixed._is_real_type(other):
            self.real += other
        elif isinstance(other, ComplexFixed):
            self.real += other.real
            self.imag += other.imag
        elif ComplexFixed._is_complex_type(other):
            trigger_error(
                'undefined',
                "In-place operations involving complex floats aren't supported"
            )
        else:
            return NotImplemented

        return self

    def __add__(self, other):
        """Adds self and a value

        Args:
            other: Value to add

        Returns:
            Result
        """

        if isinstance(
            other,
            (
                bool,
                int,
                numpy.bool,
                numpy.integer,
                mpz_type,
                Fixed,
                ComplexFixed
            )
        ):
            result = self._common_copy(other) if is_fixed_point(other) else self._create_copy()
            return result.__iadd__(other)
        elif isinstance(other, numpy.floating):
            # numpy.floating before float because numpy.double is float
            return ComplexFixed._complex_type_helper(other)(self) + other
        elif isinstance(other, numpy.complexfloating):
            return type(other)(self) + other
        elif isinstance(other, (float, complex)):
            return complex(self) + other
        elif isinstance(other, (mpmath.mpf, mpmath.mpc)):
            return self.mpmath() + other
        elif isinstance(other, (mpfr_type, mpc_type)):
            return self.mpc() + other
        else:
            return NotImplemented

    def __radd__(self, other):
        """Adds a value and self

        Args:
            other: Value to add

        Returns:
            Result
        """

        if isinstance(other, ComplexFixed):
            return NotImplemented

        return self.__add__(other)

    # Subtraction

    def __isub__(self, other) -> Self:
        """Subtracts a value from self in-place

        Args:
            other: Value to subtract

        Raises:
            FixedUndefined: If other is complex floating (consistency with other operators)

        Returns:
            ComplexFixed: self
        """

        if ComplexFixed._is_real_type(other):
            self.real -= other
        elif isinstance(other, ComplexFixed):
            self.real -= other.real
            self.imag -= other.imag
        elif ComplexFixed._is_complex_type(other):
            trigger_error(
                'undefined',
                "In-place operations involving complex floats aren't supported"
            )
        else:
            return NotImplemented

        return self

    def __sub__(self, other):
        """Subtracts self and a value

        Args:
            other: Value to subtract

        Returns:
            Result
        """

        if isinstance(
            other,
            (
                bool,
                int,
                numpy.bool,
                numpy.integer,
                mpz_type,
                Fixed,
                ComplexFixed
            )
        ):
            result = self._common_copy(other) if is_fixed_point(other) else self._create_copy()
            return result.__isub__(other)
        elif isinstance(other, numpy.floating):
            return ComplexFixed._complex_type_helper(other)(self) - other
        elif isinstance(other, numpy.complexfloating):
            return type(other)(self) - other
        elif isinstance(other, (float, complex)):
            return complex(self) - other
        elif isinstance(other, (mpmath.mpf, mpmath.mpc)):
            return self.mpmath() - other
        elif isinstance(other, (mpfr_type, mpc_type)):
            return self.mpc() - other
        else:
            return NotImplemented

    def __rsub__(self, other):
        """Subtracts a value and self

        Args:
            other: Value to subtract from

        Returns:
            Result
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            r = other - self.real
            i = -(self.imag._higher_precision())
            return self._create_common(other, r, i)\
                if is_fixed_point(other)           \
                else self._create_same(r, i)
        elif isinstance(other, numpy.floating):
            return other - ComplexFixed._complex_type_helper(other)(self)
        elif isinstance(other, numpy.complexfloating):
            return other - type(other)(self)
        elif isinstance(other, (float, complex)):
            return other - complex(self)
        elif isinstance(other, (mpmath.mpf, mpmath.mpc)):
            return other - self.mpmath()
        elif isinstance(other, (mpfr_type, mpc_type)):
            return other - self.mpc()
        else:
            return NotImplemented

    # Multiplication

    def __imul__(self, other) -> Self:
        """Multiplies self by a value in-place

        Args:
            other: Value to multiply by

        Raises:
            FixedUndefined: If other is complex floating (can't be calculated accurately without
            increasing fixed-point precision to fully match the floating point exponent)

        Returns:
            ComplexFixed: self
        """

        if ComplexFixed._is_real_type(other):
            self.real *= other
            self.imag *= other
        elif isinstance(other, ComplexFixed):
            result = self * other
            self.real = result.real
            self.imag = result.imag
        elif ComplexFixed._is_complex_type(other):
            trigger_error(
                'undefined',
                "In-place operations involving complex floats aren't supported"
            )
        else:
            return NotImplemented

        return self

    def __mul__(self, other):
        """Multiplies self with a value

        Args:
            other: Value to multiply by

        Returns:
            Result
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            result = self._common_copy(other) if is_fixed_point(other) else self._create_copy()
            return result.__imul__(other)
        elif isinstance(other, ComplexFixed):
            # (a + bi)(c + di) = ac - bd + i * (bc + ad)
            # Increase precision to avoid overflow errors

            a = self.real._higher_precision()._higher_precision()
            b = self.imag._higher_precision()._higher_precision()
            # Casting c and d to higher precision is required
            # in case other is more precise than self
            c = other.real._higher_precision()._higher_precision()
            d = other.imag._higher_precision()._higher_precision()

            result_real = a * c - b * d
            result_imag = b * c + a * d

            return self._create_common(other, result_real, result_imag)
        elif isinstance(other, numpy.floating):
            return ComplexFixed._complex_type_helper(other)(self) * other
        elif isinstance(other, numpy.complexfloating):
            return type(other)(self) * other
        elif isinstance(other, (float, complex)):
            return complex(self) * other
        elif isinstance(other, (mpmath.mpf, mpmath.mpc)):
            return self.mpmath() * other
        elif isinstance(other, (mpfr_type, mpc_type)):
            return self.mpc() * other
        else:
            return NotImplemented

    def __rmul__(self, other):
        """Multiplies a value with self

        Args:
            other: Value to multiply

        Returns:
            Result
        """

        if isinstance(other, ComplexFixed):
            return NotImplemented

        return self.__mul__(other)

    # Division

    def __itruediv__(self, other) -> Self:
        """Divides self by a value in-place

        Args:
            other: Divisor

        Raises:
            FixedUndefined: If other is complex floating (can't be calculated accurately without
            increasing fixed-point precision to fully match the floating point exponent)

        Returns:
            ComplexFixed: self
        """

        return self._div(other)

    def __truediv__(self, other):
        """Divides self by a value

        Args:
            other: Divisor

        Returns:
            Result
        """

        if isinstance(
            other,
            (
                bool,
                int,
                numpy.bool,
                numpy.integer,
                mpz_type,
                Fixed,
                ComplexFixed
            )
        ):
            result = self._common_copy(other) if is_fixed_point(other) else self._create_copy()
            return result.__itruediv__(other)
        elif isinstance(other, numpy.floating):
            return ComplexFixed._complex_type_helper(other)(self) / other
        elif isinstance(other, numpy.complexfloating):
            return type(other)(self) / other
        elif isinstance(other, (float, complex)):
            return complex(self) / other
        elif isinstance(other, (mpmath.mpf, mpmath.mpc)):
            return self.mpmath() / other
        elif isinstance(other, (mpfr_type, mpc_type)):
            return self.mpc() / other
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        """Divides a value by self

        Args:
            other: Dividend

        Returns:
            Result
        """

        if isinstance(other, (bool, int, numpy.bool, numpy.integer, mpz_type, Fixed)):
            return self._reverse_div(other)
        elif isinstance(other, numpy.floating):
            return other / ComplexFixed._complex_type_helper(other)(self)
        elif isinstance(other, numpy.complexfloating):
            return other / type(other)(self)
        elif isinstance(other, (float, complex)):
            return other / complex(self)
        elif isinstance(other, (mpmath.mpf, mpmath.mpc)):
            return other / self.mpmath()
        elif isinstance(other, (mpfr_type, mpc_type)):
            return other / self.mpc()
        else:
            return NotImplemented

    # Floor division (//)

    def __ifloordiv__(self, other) -> Self:
        """Divides self by a value and floors the result in-place

        Args:
            other: Divisor

        Raises:
            FixedUndefined: If other is complex floating (can't be calculated accurately without
            increasing fixed-point precision to fully match the floating point exponent)

        Returns:
            ComplexFixed: self

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
            other: Divisor

        Returns:
            Result

        Note:
            Underflow isn't raised
        """

        if isinstance(
            other,
            (
                bool,
                int,
                numpy.bool,
                numpy.integer,
                mpz_type,
                Fixed,
                ComplexFixed
            )
        ):
            result = self._common_copy(other) if is_fixed_point(other) else self._create_copy()
            return result.__ifloordiv__(other)
        else:
            return ComplexFixed._floordiv_helper(self, other)

    def __rfloordiv__(self, other):
        """Divides a value by self and floors the result

        Args:
            other: Dividend

        Returns:
            Result

        Note:
            Underflow isn't raised
        """

        if isinstance(
            other,
            (
                bool,
                int,
                numpy.bool,
                numpy.integer,
                mpz_type,
                Fixed
            )
        ):
            return self._reverse_div(
                other,
                rounded_bits=self.fraction_bits,
                rounding=FixedRounding.FLOOR,
                check_underflow=False
            )
        elif isinstance(other, ComplexFixed):
            return NotImplemented
        else:
            return ComplexFixed._floordiv_helper(other, self)

    # Shifts (multiply/divide by a power of 2)

    def __ilshift__(self, other) -> Self:
        """Left shift self in-place, i.e. multiply by 2 ** other

        Args:
            other (bool, int, numpy.bool, numpy.integer): Bit count to shift by. May be negative.

        Returns:
            ComplexFixed: self
        """

        self.real <<= other
        self.imag <<= other
        return self

    def __lshift__(self, other) -> Self:
        """Left shift self, i.e. multiply by 2 ** other

        Args:
            other (bool, int, numpy.bool, numpy.integer): Bit count to shift by. May be negative.

        Returns:
            ComplexFixed: Result
        """

        result = self._create_copy()
        return result.__ilshift__(other)

    def __irshift__(self, other) -> Self:
        """Right shift self in-place, i.e. divides by 2 ** other

        Args:
            other (bool, int, numpy.bool, numpy.integer): Bit count to shift by. May be negative.

        Returns:
            ComplexFixed: self
        """

        self.real >>= other
        self.imag >>= other
        return self

    def __rshift__(self, other) -> Self:
        """Right shift self, i.e. divides by 2 ** other

        Args:
            other (bool, int, numpy.bool, numpy.integer): Bit count to shift by. May be negative.

        Returns:
            ComplexFixed: Result
        """

        result = self._create_copy()
        return result.__irshift__(other)

    # Comparisons

    def cmp(self, other) -> PartialOrdering:
        """Compares ComplexFixed and another value

        Args:
            other: Value to compare against

        Returns:
            PartialOrdering: Comparison result
        """

        # Compare the components themselves

        if ComplexFixed._is_real_type(other):
            real_cmp = self.real.cmp(other)
            imag_cmp = self.imag.value
        elif ComplexFixed._is_complex_type(other):
            real_cmp = self.real.cmp(other.real)
            imag_cmp = self.imag.cmp(other.imag)
        else:
            return NotImplemented

        # nan == nan returns False
        if (real_cmp != real_cmp) or (imag_cmp != imag_cmp):
            return PartialOrdering.UNORDERED

        # Convert the results to PartialOrdering
        if real_cmp == 0 and imag_cmp == 0:
            return PartialOrdering.EQUAL
        elif real_cmp and imag_cmp:
            return PartialOrdering.UNORDERED
        elif real_cmp:
            return PartialOrdering.GREATER if real_cmp > 0 else PartialOrdering.LESS
        else:  # imag_cmp != 0
            return PartialOrdering.GREATER if imag_cmp > 0 else PartialOrdering.LESS

    def __eq__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result == PartialOrdering.EQUAL

    def __ne__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result != PartialOrdering.EQUAL

    def __lt__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result == PartialOrdering.LESS

    def __le__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result in (PartialOrdering.LESS, PartialOrdering.EQUAL)

    def __gt__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result == PartialOrdering.GREATER

    def __ge__(self, other) -> bool:
        result = self.cmp(other)
        if result is NotImplemented:
            return NotImplemented
        return result in (PartialOrdering.GREATER, PartialOrdering.EQUAL)

    # NumPy support

    def __array_ufunc__(self, ufunc, method, *args, **kwargs):
        """Internal function for NumPy.\f
           Avoids NumPy converting ComplexFixed to numpy.double.
        """

        cmp_ops = {
            numpy.equal: (
                '__eq__',
                lambda diff: diff == PartialOrdering.EQUAL
            ),
            numpy.not_equal: (
                '__ne__',
                lambda diff: diff != PartialOrdering.EQUAL
            ),
            numpy.less: (
                '__lt__',
                lambda diff: diff == PartialOrdering.GREATER
            ),
            numpy.less_equal: (
                '__le__',
                lambda diff: diff in (PartialOrdering.EQUAL, PartialOrdering.GREATER)
            ),
            numpy.greater: (
                '__gt__',
                lambda diff: diff == PartialOrdering.LESS
            ),
            numpy.greater_equal: (
                '__ge__',
                lambda diff: diff in (PartialOrdering.EQUAL, PartialOrdering.LESS)
            ),
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
        }

        if method == '__call__':
            if ufunc in ops:
                name = ops[ufunc]
                if isinstance(args[0], ComplexFixed):
                    return getattr(ComplexFixed, '__' + name)(*args)
                elif not 'shift' in name:
                    return getattr(ComplexFixed, '__r' + name)(*(args[::-1]))
                # else return NotImplemented
            elif ufunc in cmp_ops:
                if isinstance(args[0], ComplexFixed):
                    return getattr(ComplexFixed, cmp_ops[ufunc][0])(*args)
                else:
                    if args[0].size == 1:
                        return cmp_ops[ufunc][1](args[1].cmp(args[0].dtype.type(args[0])))
                    # else return NotImplemented
            elif ufunc == numpy.conj:
                return self._create_same(self.real, -self.imag)

        return NotImplemented


def is_fixed_point(x) -> bool:
    """Checks if x is a fixed-point number

    Args:
        x: Number to check

    Returns:
        bool: True if x is a fixed-point number (real or complex)
    """

    return isinstance(x, (Fixed, ComplexFixed))


class ComplexFixedAlias(FixedConfig):
    """Provides a type alias for pre-configured complex fixed-point
    """

    def __init__(self, fraction_bits: int, integer_bits: int, sign: bool, saturation: bool):
        """Creates a new alias

        Args:
            fraction_bits (int): Fraction bits
            integer_bits (int): Integer bits
            sign (bool): Signedness
            saturation (bool): Saturation
        """

        # Let Fixed check the configuration
        self.properties = Fixed(
            fraction_bits=fraction_bits,
            integer_bits=integer_bits,
            sign=sign,
            saturation=saturation
        ).properties

    def __call__(self, *args, **kwargs) -> ComplexFixed:
        """Creates a new complex fixed-point variable

        Returns:
            ComplexFixed: Variable
        """

        return ComplexFixed(
            *args,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign,
            saturation=self.saturation,
            **kwargs
        )


@functools.cache
def create_complex_alias(f: int, i: int, s: bool, sat: bool) -> ComplexFixedAlias:
    """Creates a complex fixed-point alias

    Args:
        f (int): Fraction bits
        i (int): Integer bits
        s (bool): Signedness
        sat (bool): Saturation

    Returns:
        ComplexFixedAlias: Alias
    """

    return ComplexFixedAlias(f, i, s, sat)


def complex_alias(value: ComplexFixed) -> ComplexFixedAlias:
    """Create a type alias from a complex fixed-point value

    Args:
        value (Fixed): Value to create an alias of

    Returns:
        ComplexFixedAlias: Complex fixed-point alias
    """

    if not isinstance(value, ComplexFixed):
        raise TypeError('Invalid type')

    return create_complex_alias(
        value.fraction_bits,
        value.integer_bits,
        value.sign,
        value.saturation
    )


def alias(value: Fixed | ComplexFixed) -> FixedAlias | ComplexFixedAlias:
    """Create a type alias from a (complex) fixed-point value

    Args:
        value (Fixed, ComplexFixed): Value to create an alias of

    Returns:
        FixedAlias, ComplexFixedAlias: Fixed-point alias
    """

    if isinstance(value, Fixed):
        return fixed_alias(value)
    elif isinstance(value, ComplexFixed):
        return complex_alias(value)
    else:
        raise TypeError('Invalid type')
