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

"""Tests initialization (ComplexFixed.__init__)
"""

import numpy
import math
import mpmath
import pyfixed
import pyfixed.test_utils as test_utils
import pytest


class InitTestSuite(test_utils.TestSuite):

    def _constructor(self, *args, **kwargs):
        return pyfixed.ComplexFixed(
            *args,
            **kwargs,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign,
            saturation=self.saturation
        )

    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)
        self.tests = (
            self.test_internal,
            self.test_fixed,
            self.test_bool,
            self.test_int,
            self.test_mpz,
            self.test_numpy_int,
            (self.test_float, float),
            (self.test_float, numpy.float32),
            (self.test_float, numpy.float64),
            (self.test_float, numpy.float128),
            self.test_mpf,
            self.test_mpfr,
        )

    def test_internal(self):
        """Tests initialization from an internal value
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign,
            self.saturation
        ):
            c = self._constructor(value.value, internal=True)
            assert c.real.value == value.value
            assert c.imag.value == 0

            c = self._constructor(0, value.value, internal=True)
            assert c.real.value == 0
            assert c.imag.value == value.value

            c = self._constructor(value.value, value.value, internal=True)
            assert c.real.value == value.value
            assert c.imag.value == value.value

    def test_fixed(self):
        """Test initialization from a fixed value
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign,
            self.saturation
        ):
            c = self._constructor(value)
            assert c.real.value == value.value
            assert c.imag.value == 0

            c = self._constructor(0, value)
            assert c.real.value == 0
            assert c.imag.value == value.value

            c = self._constructor(value, value)
            assert c.real.value == value.value
            assert c.imag.value == value.value

            c = self._constructor(c)
            assert c.real.value == value.value
            assert c.imag.value == value.value

            # Test Fixed(ComplexFixed)
            assert pyfixed.Fixed(
                c,
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                self.saturation
            ).value == value.value
            assert pyfixed.Fixed(c).value == value.value

    def test_bool(self):
        """Test initialization from booleans (Python and NumPy)
        """

        if self.integer_bits == 0:
            if self.saturation:
                test_utils.behavior_check('overflow', lambda: self._constructor(True).real)
                test_utils.behavior_check('overflow', lambda: self._constructor(0, True).imag)

                test_utils.behavior_check(
                    'overflow', lambda: self._constructor(numpy.bool(True)).real)
                test_utils.behavior_check(
                    'overflow',
                    lambda: self._constructor(0, numpy.bool(True)).imag
                )

                test_utils.behavior_check(
                    'overflow',
                    lambda: self._constructor(True, True).real
                )
                test_utils.behavior_check(
                    'overflow',
                    lambda: self._constructor(True, True).imag
                )

                test_utils.behavior_check(
                    'overflow',
                    lambda: self._constructor(numpy.bool(True), numpy.bool(True)).real
                )
                test_utils.behavior_check(
                    'overflow',
                    lambda: self._constructor(numpy.bool(True), numpy.bool(True)).imag
                )
            else:
                assert self._constructor(True).real.value == self._min_val

                assert self._constructor(0, True).imag.value == self._min_val

                c = self._constructor(True, True)
                assert c.real.value == self._min_val
                assert c.imag.value == self._min_val

                assert self._constructor(numpy.bool(True)).real.value == self._min_val

                assert self._constructor(0, numpy.bool(True)).imag.value == self._min_val

                c = self._constructor(numpy.bool(True), numpy.bool(True))
                assert c.real.value == self._min_val
                assert c.imag.value == self._min_val

            with pyfixed.with_partial_state(overflow_behavior=pyfixed.FixedBehavior.IGNORE):
                assert self._constructor(True).imag.value == 0
                assert self._constructor(0, True).real.value == 0

                assert self._constructor(numpy.bool(True)).imag.value == 0
                assert self._constructor(0, numpy.bool(True)).real.value == 0

            c = self._constructor(False)
            assert c.real.value == 0
            assert c.imag.value == 0

            c = self._constructor(0, False)
            assert c.real.value == 0
            assert c.imag.value == 0

            c = self._constructor(False, False)
            assert c.real.value == 0
            assert c.imag.value == 0

            c = self._constructor(numpy.bool(False))
            assert c.real.value == 0
            assert c.imag.value == 0

            c = self._constructor(0, numpy.bool(False))
            assert c.real.value == 0
            assert c.imag.value == 0

            c = self._constructor(numpy.bool(False), numpy.bool(False))
            assert c.real.value == 0
            assert c.imag.value == 0
        else:
            for value in (False, True, numpy.bool(False), numpy.bool(True)):
                expected = pyfixed.backend(value) << self.fraction_bits

                c = self._constructor(value)
                assert c.real.value == expected
                assert c.imag.value == 0

                c = self._constructor(0, value)
                assert c.real.value == 0
                assert c.imag.value == expected

                c = self._constructor(value, value)
                assert c.real.value == expected
                assert c.imag.value == expected

    def test_int(self):
        """Test initialization from Python integers
        """

        if self.integer_bits + self.sign > 0:
            for value in test_utils.fixed_range(
                0,
                self.integer_bits,
                self.sign,
                self.saturation
            ):
                expected = value.value << self.fraction_bits

                c = self._constructor(int(value.value))
                assert c.real.value == expected
                assert c.imag.value == 0

                c = self._constructor(0, int(value.value))
                assert c.real.value == 0
                assert c.imag.value == expected

                c = self._constructor(int(value.value), int(value.value))
                assert c.real.value == expected
                assert c.imag.value == expected

    def test_mpz(self):
        """Test initialization from gmpy2.mpz
        """

        if pyfixed.mpz_type is not int and self.integer_bits + self.sign > 0:
            for value in test_utils.fixed_range(
                0,
                self.integer_bits,
                self.sign,
                self.saturation
            ):
                expected = value.value << self.fraction_bits

                c = self._constructor(pyfixed.mpz_type(value.value))
                assert c.real.value == expected
                assert c.imag.value == 0

                c = self._constructor(0, pyfixed.mpz_type(value.value))
                assert c.real.value == 0
                assert c.imag.value == expected

                c = self._constructor(pyfixed.mpz_type(value.value), pyfixed.mpz_type(value.value))
                assert c.real.value == expected
                assert c.imag.value == expected

    def test_numpy_int(self):
        """Test initialization from NumPy integers
        """

        int_bits = self.integer_bits + self.sign
        if int_bits > 0 and int_bits <= 64:
            for value in test_utils.fixed_range(
                0,
                self.integer_bits,
                self.sign,
                self.saturation
            ):
                v = (numpy.int64 if self.sign else numpy.uint64)(value.value)
                expected = value.value << self.fraction_bits

                c = self._constructor(v)
                assert c.real.value == expected
                assert c.imag.value == 0

                c = self._constructor(0, v)
                assert c.real.value == 0
                assert c.imag.value == expected

                c = self._constructor(v, v)
                assert c.real.value == expected
                assert c.imag.value == expected

    def test_float(self, float_type: type):
        """Test initialization from floating point

        Args:
            float_type (type): Type to initialize from
        """

        if self.precision <= numpy.finfo(float_type).nmant + 1:
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                self.saturation
            ):
                f = math.ldexp(value.value, -self.fraction_bits)            \
                    if float_type is float else                             \
                    numpy.ldexp(float_type(value.value), -self.fraction_bits)

                c = self._constructor(f)
                assert c.real.value == value.value
                assert c.imag.value == 0

                c = self._constructor(0, f)
                assert c.real.value == 0
                assert c.imag.value == value.value

                c = self._constructor(f, f)
                assert c.real.value == value.value
                assert c.imag.value == value.value

                c = self._constructor(f + 1j * f)
                assert c.real.value == value.value
                assert c.imag.value == value.value

    def test_mpf(self):
        """Test initialization from mpmath.mpf and mpmath.mpc
        """

        with mpmath.workprec(self.precision + 1):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                self.saturation
            ):
                f = mpmath.ldexp(value.value, -self.fraction_bits)

                c = self._constructor(f)
                assert c.real.value == value.value
                assert c.imag.value == 0

                c = self._constructor(0, f)
                assert c.real.value == 0
                assert c.imag.value == value.value

                c = self._constructor(f, f)
                assert c.real.value == value.value
                assert c.imag.value == value.value

                c = self._constructor(mpmath.mpc(f, f))
                assert c.real.value == value.value
                assert c.imag.value == value.value

    def test_mpfr(self):
        """Test initialization from gmpy2
        """

        if pyfixed.mpfr_type is not float:
            with pyfixed.gmpy2.context(pyfixed.gmpy2.get_context()) as ctx:
                ctx.precision = self.precision + 1
                for value in test_utils.fixed_range(
                    self.fraction_bits,
                    self.integer_bits,
                    self.sign,
                    self.saturation
                ):
                    f = pyfixed.mpfr_type(value.value) * pyfixed.gmpy2.exp2(-self.fraction_bits)

                    c = self._constructor(f)
                    assert c.real.value == value.value
                    assert c.imag.value == 0

                    c = self._constructor(0, f)
                    assert c.real.value == 0
                    assert c.imag.value == value.value

                    c = self._constructor(f, f)
                    assert c.real.value == value.value
                    assert c.imag.value == value.value

                    c = self._constructor(pyfixed.mpc_type(f, f))
                    assert c.real.value == value.value
                    assert c.imag.value == value.value


test_all = test_utils.run_tests(InitTestSuite)


def test_config():
    """Tests configuration
    """

    deduced = pyfixed.ComplexFixed()
    assert deduced.real.value == 0 and deduced.imag.value == 0

    fraction_bits = 9
    integer_bits = 10
    sign = True
    saturation = True

    base = pyfixed.ComplexFixed(
        fraction_bits=fraction_bits,
        integer_bits=integer_bits,
        sign=sign,
        saturation=True
    )

    deduced = pyfixed.ComplexFixed(base)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits and     \
        deduced.sign == sign and                     \
        deduced.saturation == saturation

    deduced = pyfixed.ComplexFixed(base, fraction_bits=fraction_bits + 1)
    assert deduced.fraction_bits == fraction_bits + 1 and\
        deduced.integer_bits == integer_bits and         \
        deduced.sign == sign and                         \
        deduced.saturation == saturation

    deduced = pyfixed.ComplexFixed(base, integer_bits=integer_bits + 1)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits + 1 and \
        deduced.sign == sign and                     \
        deduced.saturation == saturation

    deduced = pyfixed.ComplexFixed(base, sign=not sign)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits and     \
        deduced.sign == (not sign) and               \
        deduced.saturation == saturation

    deduced = pyfixed.ComplexFixed(base, saturation=not saturation)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits and     \
        deduced.sign == sign and                     \
        deduced.saturation == (not saturation)

    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(fraction_bits=-1)
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(integer_bits=-1)
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(fraction_bits=0, integer_bits=0, sign=False)
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(0j, 0)
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(0, 0j)
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(numpy.cdouble(0), 0)
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(0, numpy.cdouble(0))
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(mpmath.mpc(), 0)
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(0, mpmath.mpc())
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(pyfixed.mpc_type(), 0)
    with pytest.raises(TypeError):
        _ = pyfixed.ComplexFixed(0, pyfixed.mpc_type())
