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

"""Tests initialization (Fixed.__init__)
"""

import numpy
import mpmath
import pyfixed
import pyfixed.test_utils as test_utils
import pytest


class InitTestSuite(test_utils.TestSuite):

    def _constructor(self, *args, **kwargs):
        return pyfixed.Fixed(
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
            *(
                (
                    self.test_fixed,
                    mode,
                    (
                        test_utils.fixed_range,
                        *(config if config != (0, 0) else (0, 1)),
                        sign,
                        saturation
                    )
                )
                for mode in pyfixed.FixedRounding
                for saturation in (False, True)
                for sign in (False, True)
                for config in (
                    (self.fraction_bits, self.integer_bits),
                    (2 * (self.fraction_bits + 1), 2 * (self.integer_bits + 1)),
                    (self.fraction_bits // 2, self.integer_bits // 2),
                )
            ),
            self.test_bool,
            *(
                (self.test_int, t)
                for t in (
                    int,
                    numpy.int8,
                    numpy.uint8,
                    numpy.int16,
                    numpy.uint16,
                    numpy.int32,
                    numpy.uint32,
                    numpy.int64,
                    numpy.uint64,
                )
            ),
            (self.test_int, pyfixed.mpz_type) if pyfixed.mpz_type is not int else lambda: (),
            *(
                (self.test_float, mode, rhs)
                for rhs in test_utils.FLOAT_RANGES
                for mode in pyfixed.FixedRounding
                if rhs is not None
            ),
            self.test_complex,
        )

    def test_internal(self):
        """Tests initialization from an internal value
        """

        step = max(
            (2 ** self.bits // test_utils.TEST_INT_RANGE_SAMPLES)
            if test_utils.TEST_INT_RANGE_SAMPLES
            else 1,
            1
        )

        for idx, value in enumerate(
            test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                self.saturation
            )
        ):
            assert idx * step + self._min_val == value.value

    def test_fixed(self, mode: pyfixed.FixedRounding, rhs: list | tuple):
        """Test initialization from a fixed value

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to use
            rhs (list, tuple): Generator function and its arguments
        """

        limit = 1 << self.bits
        half_limit = limit >> 1
        mask = limit - 1

        rounder = test_utils.rounding_modes[mode]

        with mpmath.workprec(2 * (self.fraction_bits + 1) + 2 * (self.integer_bits + 1) + 1), \
                pyfixed.with_partial_state(rounding=mode):
            for value in rhs[0](*(rhs[1::])):
                expected = int(
                    rounder(
                        mpmath.ldexp(
                            value.value,
                            self.fraction_bits - value.fraction_bits
                        )
                    )
                )

                if self.saturation and (expected > self._max_val or expected < self._min_val):
                    with pytest.raises(pyfixed.FixedOverflow):
                        self._constructor(value)
                    with pyfixed.with_partial_state(
                        overflow_behavior=pyfixed.FixedBehavior.IGNORE
                    ):
                        assert self._constructor(value).value == \
                            (self._max_val if expected > 0 else self._min_val)
                    continue

                if value.value and expected == 0:
                    with pytest.raises(pyfixed.FixedUnderflow):
                        self._constructor(value)
                    with pyfixed.with_partial_state(
                        underflow_behavior=pyfixed.FixedBehavior.IGNORE
                    ):
                        assert self._constructor(value).value == 0
                    continue

                if not self.saturation:
                    expected = expected & mask
                    if self.sign and expected >= half_limit:
                        expected -= limit

                assert self._constructor(value).value == expected

    def test_bool(self):
        """Test initialization from booleans (Python and NumPy)
        """

        if self.integer_bits == 0:
            if self.saturation:
                test_utils.behavior_check('overflow', lambda: self._constructor(True))
            else:
                assert self._constructor(True).value == self._min_val
            assert self._constructor(False).value == 0
        else:
            for value in (False, True):
                assert self._constructor(value).value == (int(value) << self.fraction_bits)
                assert self._constructor(numpy.bool(value)).value == \
                    (int(value) << self.fraction_bits)

    def test_int(self, t: type):
        """Test initialization from integers

        Args:
            t (type): Integer type to test
        """

        for value in test_utils.int_range(t):
            expected = pyfixed.backend(value) << self.fraction_bits
            if self.saturation:
                if expected > self._max_val or expected < self._min_val:
                    with pytest.raises(pyfixed.FixedOverflow):
                        _ = self._constructor(value)
                    with pyfixed.with_partial_state(
                        overflow_behavior=pyfixed.FixedBehavior.IGNORE
                    ):
                        assert self._constructor(value).value == \
                            (self._max_val if value > 0 else self._min_val)
                else:
                    assert self._constructor(value).value == expected
            else:
                assert self._constructor(value).value == \
                    pyfixed.simulate_overflow(expected, self.bits, self.sign)

    def test_float(self, mode: pyfixed.FixedRounding, rhs: list | tuple):
        """Test initialization from floating point

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to use
            rhs (list, tuple): Generator function and its arguments
        """

        limit = 1 << self.bits

        rounder = test_utils.rounding_modes[mode]

        with mpmath.workprec(max(numpy.finfo(numpy.float128).nmant + 1, self.bits)), \
                pyfixed.with_partial_state(rounding=mode):
            for value in rhs[0](*(rhs[1::])):
                if pyfixed.float_is_nan(value):
                    with pytest.raises(pyfixed.FixedUndefined):
                        self._constructor(value)
                    with pyfixed.with_partial_state(
                        undefined_behavior=pyfixed.FixedBehavior.IGNORE
                    ):
                        assert self._constructor(value).value == 0
                    continue

                offset_value = rounder(
                    mpmath.ldexp(
                        pyfixed.mpfr_to_mpf(value)
                        if pyfixed.mpfr_type is not float and isinstance(value, pyfixed.mpfr_type)
                        else mpmath.mpmathify(value),
                        self.fraction_bits
                    )
                )

                if value and offset_value == 0:
                    with pytest.raises(pyfixed.FixedUnderflow):
                        self._constructor(value)
                    with pyfixed.with_partial_state(
                        underflow_behavior=pyfixed.FixedBehavior.IGNORE
                    ):
                        assert self._constructor(value).value == 0
                    continue

                if self.saturation:
                    if offset_value > self._max_val or offset_value < self._min_val:
                        with pytest.raises(pyfixed.FixedOverflow):
                            self._constructor(value)
                        with pyfixed.with_partial_state(
                            overflow_behavior=pyfixed.FixedBehavior.IGNORE
                        ):
                            assert self._constructor(value).value == \
                                (self._max_val if offset_value > 0 else self._min_val)
                        continue
                    else:
                        expected = offset_value
                else:
                    if pyfixed.float_is_inf(value):
                        expected = 0
                    else:
                        expected = offset_value % limit
                        if self.sign and expected >= (limit >> 1):
                            expected -= limit

                assert self._constructor(value).value == expected

    def test_complex(self):
        assert self._constructor(1j).value == 0


test_all = test_utils.run_tests(InitTestSuite)


def test_config():
    """Tests configuration
    """

    assert pyfixed.Fixed().value == 0

    fraction_bits = 9
    integer_bits = 10
    sign = True
    saturation = True

    base = pyfixed.Fixed(
        fraction_bits=fraction_bits,
        integer_bits=integer_bits,
        sign=sign,
        saturation=saturation
    )

    deduced = pyfixed.Fixed(base)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits and     \
        deduced.sign == sign and                     \
        deduced.saturation == saturation

    deduced = pyfixed.Fixed(base, fraction_bits=fraction_bits + 1)
    assert deduced.fraction_bits == fraction_bits + 1 and\
        deduced.integer_bits == integer_bits and         \
        deduced.sign == sign and                         \
        deduced.saturation == saturation

    deduced = pyfixed.Fixed(base, integer_bits=integer_bits + 1)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits + 1 and \
        deduced.sign == sign and                     \
        deduced.saturation == saturation

    deduced = pyfixed.Fixed(base, sign=not sign)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits and     \
        deduced.sign == (not sign) and               \
        deduced.saturation == saturation

    deduced = pyfixed.Fixed(base, saturation=not saturation)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits and     \
        deduced.sign == sign and                     \
        deduced.saturation == (not saturation)

    with pytest.raises(TypeError):
        _ = pyfixed.Fixed(fraction_bits=-1)
    with pytest.raises(TypeError):
        _ = pyfixed.Fixed(integer_bits=-1)
    with pytest.raises(TypeError):
        _ = pyfixed.Fixed(fraction_bits=0, integer_bits=0, sign=False)
