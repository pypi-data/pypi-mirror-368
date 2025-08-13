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

"""Tests utility functions
"""

import math
import mpmath
import numpy
import pyfixed
import pyfixed.test_utils as test_utils
import pytest


class UtilTestSuite(test_utils.TestSuite):
    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)

        self.workprec = max(
            2 * self.precision,
            # mpmath rounds to even internally, so to avoid that we need to
            # be able to represent every possible input with exact precision
            numpy.finfo(numpy.float128).nmant + 1
        )

        fixed_min = pyfixed.Fixed(
            value=self._min_val,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign,
            internal=True
        )
        fixed_max = pyfixed.Fixed(
            value=self._max_val,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign,
            internal=True
        )

        fixed_int_range = (4 * math.floor(fixed_min), 4 * (math.ceil(fixed_max) + 1)) \
            if test_utils.TEST_INT_RANGE_SAMPLES == 0 \
            else tuple()

        self.int_ranges = (
            # Same type
            (
                test_utils.fixed_range,
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                True
            ),
            # Bigger fixed
            (
                test_utils.fixed_range,
                self.bits,
                self.bits,
                True,
                True
            ),
            # Smaller fixed
            (
                test_utils.fixed_range,
                self.fraction_bits // 2,
                self.integer_bits // 2,
                True,
                True
            ),
            # Unsaturated
            (
                test_utils.fixed_range,
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                False
            ),
            (
                test_utils.fixed_range,
                self.bits,
                self.bits,
                True,
                False
            ),
            (
                test_utils.fixed_range,
                self.fraction_bits // 2,
                self.integer_bits // 2,
                True,
                False
            ),
            # Integral types
            (test_utils.iterator, False, True),
            (test_utils.int_range, int, *fixed_int_range),
            (test_utils.iterator, numpy.bool(False), numpy.bool(True)),
            (test_utils.int_range, numpy.int64, *fixed_int_range),
            (test_utils.int_range, numpy.uint64, *fixed_int_range),
            (test_utils.int_range, pyfixed.mpz_type, *fixed_int_range)
            if pyfixed.mpz_type is not int
            else None,
        )

        self.ranges = self.int_ranges + test_utils.FLOAT_RANGES

        self.tests = (
            self.frexp_test,
            self.modf_test,
            self.ilogb_test,
            *(
                (self.copysign_test, rhs)
                for rhs in self.ranges
            ),
            *(
                (self.nextafter_test, rhs)
                for rhs in self.ranges
            ),
        )

    def frexp_test(self):
        """Tests frexp
        """

        with mpmath.workprec(self.precision):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                self.saturation
            ):
                f, e = pyfixed.frexp(value)

                assert isinstance(e, int)

                if self.fraction_bits == 0 and self.integer_bits == 0:
                    # frexp can't handle Fixed<0, 0, True>
                    assert f.fraction_bits == 0 and f.integer_bits == 0 and f.sign == True
                    assert f.value == value.value
                else:
                    assert f.fraction_bits == self.precision and f.integer_bits == 0 and f.sign == self.sign
                    f = f.mpmath()
                    assert (f, e) == mpmath.frexp(value.mpmath())

    def modf_test(self):
        """Tests modf
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign,
            self.saturation
        ):
            f, i = pyfixed.modf(value)
            assert i == math.trunc(value)
            assert i + f == value

    def copysign_test(self, rhs_range: list | tuple):
        """Tests copysign

        Args:
            rhs_range (list, tuple): RHS range function and its parameters
        """

        if rhs_range is None:
            return

        for lhs in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign,
            self.saturation
        ):
            for rhs in rhs_range[0](*(rhs_range[1:])):
                rhs_sign = rhs < 0

                if isinstance(rhs, (float, numpy.floating)):
                    rhs_sign = numpy.signbit(rhs)
                elif isinstance(rhs, pyfixed.mpfr_type):
                    rhs_sign = rhs.is_signed()

                same_sign = rhs_sign == (lhs < 0)

                if self.sign and lhs.value == lhs._min_val and not rhs_sign or \
                        not self.sign and rhs_sign and lhs.value:
                    if self.saturation:
                        with pytest.raises(pyfixed.FixedOverflow):
                            _ = pyfixed.copysign(lhs, rhs)
                        with pyfixed.with_partial_state(
                            overflow_behavior=pyfixed.FixedBehavior.IGNORE
                        ):
                            assert pyfixed.copysign(lhs, rhs).value == \
                                (lhs._max_val if self.sign else 0)
                    else:
                        assert pyfixed.copysign(lhs, rhs).value == \
                            (lhs.value if self.sign else (-lhs.value & ((1 << lhs.bits) - 1)))
                else:
                    assert pyfixed.copysign(lhs, rhs).value == (lhs if same_sign else -lhs).value

                if isinstance(rhs, pyfixed.Fixed) and (
                    rhs.sign and rhs.value == rhs._min_val and lhs >= 0 or
                    not rhs.sign and lhs < 0 and rhs.value
                ):
                    if rhs.saturation:
                        with pytest.raises(pyfixed.FixedOverflow):
                            _ = pyfixed.copysign(rhs, lhs)
                        with pyfixed.with_partial_state(overflow_behavior=pyfixed.FixedBehavior.IGNORE):
                            assert pyfixed.copysign(rhs, lhs).value == \
                                (rhs._max_val if rhs.sign else 0)
                    else:
                        assert pyfixed.copysign(rhs, lhs).value == \
                            (rhs.value if rhs.sign else (-rhs.value & ((1 << rhs.bits) - 1)))
                elif isinstance(rhs, numpy.bool):
                    assert pyfixed.copysign(rhs, lhs) == \
                        (-bool(rhs) if lhs < 0 else rhs)
                else:
                    actual = pyfixed.copysign(rhs, lhs)
                    expected = rhs if same_sign else -rhs
                    assert actual == expected or \
                        pyfixed.float_is_nan(actual) == pyfixed.float_is_nan(expected)

    def nextafter_test(self, rhs_range):
        """Tests nextafter

        Args:
            rhs_range (list, tuple): RHS range function and its parameters
        """

        if rhs_range is None:
            return

        for lhs in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign,
            self.saturation
        ):
            for rhs in rhs_range[0](*(rhs_range[1:])):
                if pyfixed.float_is_nan(rhs):
                    with pytest.raises(pyfixed.FixedUndefined):
                        pyfixed.nextafter(lhs, rhs)
                    with pyfixed.with_partial_state(
                        undefined_behavior=pyfixed.FixedBehavior.IGNORE
                    ):
                        assert pyfixed.nextafter(lhs, rhs) == pyfixed.fixed_alias(lhs)(math.nan)

                    assert pyfixed.float_is_nan(pyfixed.nextafter(rhs, lhs))
                else:
                    if lhs == rhs:
                        assert pyfixed.nextafter(lhs, rhs) == lhs
                        assert pyfixed.nextafter(rhs, lhs) == rhs
                    else:
                        dir = -mpmath.inf if lhs > rhs else mpmath.inf
                        dir_sign = -int(mpmath.sign(dir))  # Negated because only RHS uses it

                        def test_fixed(l: pyfixed.Fixed, r: pyfixed.Fixed, d: mpmath.mpf):
                            if l.saturation:
                                try:
                                    actual = pyfixed.nextafter(l, r)
                                    assert actual.value == l.value + int(mpmath.sign(d))
                                except pyfixed.FixedOverflow:
                                    assert l.value == l._max_val and d > 0 or \
                                        l.value == l._min_val and d < 0
                                    with pyfixed.with_partial_state(
                                        overflow_behavior=pyfixed.FixedBehavior.IGNORE
                                    ):
                                        assert pyfixed.nextafter(l, r).value == \
                                            (l._max_val if d > 0 else l._min_val)
                            else:
                                assert pyfixed.nextafter(l, r).value == \
                                    pyfixed.simulate_overflow(
                                        l.value + int(mpmath.sign(d)),
                                    l.bits,
                                    l.sign
                                )

                        test_fixed(lhs, rhs, dir)

                        if isinstance(rhs, pyfixed.Fixed):
                            test_fixed(rhs, lhs, -dir)
                        elif isinstance(rhs, (bool, numpy.bool)):
                            assert pyfixed.nextafter(rhs, lhs) == (not rhs)
                        elif isinstance(rhs, (int, pyfixed.mpz_type)):
                            assert pyfixed.nextafter(rhs, lhs) == rhs + dir_sign
                        elif isinstance(rhs, numpy.integer):
                            assert pyfixed.nextafter(rhs, lhs) == \
                                (
                                    (rhs + type(rhs)(1))
                                    if dir_sign > 0
                                    else (rhs - type(rhs)(1))
                            )
                        elif isinstance(rhs, (float, numpy.floating)):
                            actual = pyfixed.nextafter(rhs, lhs)
                            expected = numpy.nextafter(rhs, dir_sign * numpy.inf)
                            assert actual == expected or \
                                numpy.isnan(actual) == numpy.isnan(expected)
                        elif isinstance(rhs, mpmath.mpf):
                            actual = pyfixed.nextafter(rhs, lhs)
                            expected = test_utils.mpmath_nextafter(rhs, -dir)
                            assert actual == expected or \
                                mpmath.isnan(actual) == mpmath.isnan(expected)
                        elif isinstance(rhs, pyfixed.mpfr_type):
                            actual = pyfixed.nextafter(rhs, lhs)
                            expected = pyfixed.gmpy2.next_toward(
                                rhs,
                                pyfixed.gmpy2.inf(dir_sign)
                            )
                            assert actual == expected or \
                                pyfixed.gmpy2.is_nan(actual) == pyfixed.gmpy2.is_nan(expected)
                        else:
                            assert False

    def ilogb_test(self):
        """Tests ilogb
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign,
            self.saturation
        ):
            if value.value:
                assert pyfixed.ilogb(value) == mpmath.floor(mpmath.log(abs(value.mpmath()), 2))
            else:
                with pytest.raises(pyfixed.FixedUndefined):
                    _ = pyfixed.ilogb(value)
                with pyfixed.with_partial_state(undefined_behavior=pyfixed.FixedBehavior.IGNORE):
                    assert mpmath.isnan(pyfixed.ilogb(value))


test = test_utils.run_tests(UtilTestSuite)
