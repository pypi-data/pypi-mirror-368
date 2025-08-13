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

"""Tests rounding (e.g. floor(ComplexFixed) round(ComplexFixed) etc.)
"""

import math
import mpmath
import pyfixed
import pyfixed.test_utils as test_utils


class RoundingTestSuite(test_utils.TestSuite):
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
            self.test_floor,
            self.test_ceil,
            self.test_trunc,
            *(
                (self.test_round, None, mode)
                for mode in pyfixed.FixedRounding
            ),
            *(
                (self.test_round, ndigits, mode)
                for ndigits in range(-self.integer_bits, self.fraction_bits + 2)
                for mode in pyfixed.FixedRounding
            ),
        )

    def test_floor(self):
        """Test complex fixed-point flooring
        """

        with mpmath.workprec(max(self.precision, 1)):
            for value in self._range():
                r, i = math.floor(value)
                c_mp = mpmath.floor(value.mpmath())
                assert r == c_mp.real
                assert i == c_mp.imag

    def test_ceil(self):
        """Test complex fixed-point ceiling
        """

        with mpmath.workprec(max(self.precision, 1)):
            for value in self._range():
                r, i = math.ceil(value)
                c_mp = mpmath.ceil(value.mpmath())
                assert r == c_mp.real
                assert i == c_mp.imag

    def test_trunc(self):
        """Test complex fixed-point truncating
        """

        with mpmath.workprec(max(self.precision, 1)):
            for value in self._range():
                r, i = math.trunc(value)
                c_mp = test_utils.mpmath_trunc(value.mpmath())
                assert r == c_mp.real
                assert i == c_mp.imag

    def test_round(self, ndigits: int, mode: pyfixed.FixedRounding):
        """Test rounding to closest integer

        Args:
            ndigits (int): Number of binary digits after the point to round to
            mode (pyfixed.FixedRounding): Rounding mode
        """

        with pyfixed.with_partial_state(
            rounding=mode,
            overflow_behavior=pyfixed.FixedBehavior.IGNORE
        ):
            for value in self._range():

                r_v = round(value.real, ndigits)
                i_v = round(value.imag, ndigits)

                if ndigits is None:
                    r, i = round(value, ndigits)
                    assert r == r_v
                    assert i == i_v
                else:
                    c = round(value, ndigits)
                    assert c.real == r_v
                    assert c.imag == i_v


test = test_utils.run_tests(RoundingTestSuite)
