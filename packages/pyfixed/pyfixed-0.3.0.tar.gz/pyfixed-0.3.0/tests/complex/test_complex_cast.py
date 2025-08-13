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

"""Tests casting (e.g. int(ComplexFixed) float(ComplexFixed) etc.)
"""

import numpy
import mpmath
import pyfixed
import pyfixed.test_utils as test_utils
import pytest


class CastTestSuite(test_utils.TestSuite):
    def _range(self):
        """Generates a range of samples according to this class' configuration

        Returns:
            generator: Generator for
            ``ComplexFixed<self.fraction_bits, self.integer_bits, self.sign, self.saturation>``
        """

        return test_utils.complex_range(
            test_utils.fixed_range,
            pyfixed.ComplexFixed,
            self.fraction_bits,
            self.integer_bits,
            self.sign,
            self.saturation
        )

    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)
        self.tests = (
            self.test_bool,
            *(
                (self.test_int, m, t)
                for m in pyfixed.FixedRounding
                for t in (
                    int,
                    pyfixed.mpz_type if pyfixed.mpz_type is not int else None,
                    numpy.int8,
                    numpy.uint8,
                    numpy.int16,
                    numpy.uint16,
                    numpy.int32,
                    numpy.uint32,
                    numpy.int64,
                    numpy.uint64,
                )
                if t is not None
            ),
            *(
                (self.test_float, mode, t)
                for mode in pyfixed.FixedRounding
                for t in (
                    float,
                    numpy.float32,
                    numpy.float64,
                    numpy.float128,
                )
            ),
            *((self.test_mpf, m) for m in pyfixed.FixedRounding),
            *(
                ((self.test_mpfr, m) for m in pyfixed.FixedRounding)
                if pyfixed.mpfr_type is not float
                else (lambda: (),)
            ),
            self.test_str,
            self.test_bytes,
        )

    def test_bool(self):
        """Tests boolean casting
        """

        for value in self._range():
            v = bool(value)
            assert v == (bool(value.real) or bool(value.imag))
            assert numpy.bool(value) == v

    def test_int(self, mode: pyfixed.FixedRounding, t: type):
        """Tests integer casting

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to test
            t (type): Type to test casting to
        """

        if issubclass(t, numpy.integer):
            max_val = numpy.iinfo(t).max
            min_val = numpy.iinfo(t).min
        else:
            max_val = mpmath.inf
            min_val = -mpmath.inf

        with mpmath.workprec(max(self.precision, 1)), \
                pyfixed.with_partial_state(rounding=mode):
            for value in self._range():
                expected = int(value.real)

                if expected > max_val or expected < min_val:
                    with pytest.raises(OverflowError):
                        t(value)
                else:
                    assert t(value) == expected

    def test_float(self, mode: pyfixed.FixedRounding, t: type):
        """Tests float casting

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to test
            t (type): Floating-point type to test casting to
        """

        c = type(t() + 1j)

        with mpmath.workprec(numpy.finfo(t).nmant + 1), \
                pyfixed.with_partial_state(rounding=mode):
            for value in self._range():
                assert t(value) == value.real.mpmath()
                assert c(value) == t(value.real) + 1j * t(value.imag)

    def test_mpf(self, mode: pyfixed.FixedRounding):
        """Tests mpmath casting

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to test
        """

        with pyfixed.with_partial_state(rounding=mode), \
                mpmath.workprec(max(self.precision, 1)):
            for value in self._range():
                assert value.mpmath() == mpmath.mpc(value.real, value.imag)

    def test_mpfr(self, mode: pyfixed.FixedRounding):
        """Tests gmpy2 casting

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to test
        """

        with pyfixed.gmpy2.context(pyfixed.gmpy2.get_context()) as ctx, \
                pyfixed.with_partial_state(rounding=mode):
            ctx.precision = max(self.precision, 1)
            for value in self._range():
                assert value.mpfr() == value.real.mpfr()
                assert value.mpc() == pyfixed.mpc_type(
                    value.real.mpfr(),
                    value.imag.mpfr()
                )

    def test_str(self):
        """Tests string casting
        """

        for value in self._range():
            i_sign = "-" if value.imag < 0 else "+"
            r, i = str(value).split(i_sign + ' 1j * ')
            assert float(value) == float.fromhex(r)
            assert float(value.imag) == float.fromhex(i_sign + i)

    def test_bytes(self):
        """Tests byte casting
        """

        for value in self._range():
            assert bytes(value) == bytes(value.real) + bytes(value.imag)


test = test_utils.run_tests(CastTestSuite)


def test_no_gmpy2():
    """Tests that gmpy2 casting fails when gmpy2 isn't imported
    """

    if pyfixed.mpz_type is int:
        with pytest.raises(ModuleNotFoundError):
            pyfixed.ComplexFixed().mpz()

        with pytest.raises(ModuleNotFoundError):
            pyfixed.ComplexFixed().mpfr()

        with pytest.raises(ModuleNotFoundError):
            pyfixed.ComplexFixed().mpc()
