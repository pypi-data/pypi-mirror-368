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

"""Tests complex arithmetics
"""

import math
import mpmath
import numpy
import pyfixed
import pyfixed.test_utils as test_utils
import pytest

# Operations dictionary for mpmath - similar to fixed/test_arith.py
OP_DICT = {
    '__iadd__': lambda a, b: a + b,
    '__isub__': lambda a, b: a - b,
    '__imul__': lambda a, b: a * b,
    '__itruediv__': lambda a, b: a / b,
    '__ifloordiv__': lambda a, b: mpmath.floor(a / b),
    '__floordiv__': lambda a, b: mpmath.floor(a / b),
    '__rfloordiv__': lambda a, b: mpmath.floor(b / a),
    '__ilshift__': test_utils.complex_ldexp,
    '__lshift__': test_utils.complex_ldexp,
    '__irshift__': lambda a, b: test_utils.complex_ldexp(a, -b),
    '__rshift__': lambda a, b: test_utils.complex_ldexp(a, -b),
    '__lt__': lambda a, b: test_utils.complex_cmp(a, b, '__lt__'),
    '__le__': lambda a, b: test_utils.complex_cmp(a, b, '__le__'),
    '__gt__': lambda a, b: test_utils.complex_cmp(a, b, '__gt__'),
    '__ge__': lambda a, b: test_utils.complex_cmp(a, b, '__ge__'),
    '__req__': lambda a, b: b == a,
    '__rne__': lambda a, b: b != a,
    '__rlt__': lambda a, b: test_utils.complex_cmp(b, a, '__lt__'),
    '__rle__': lambda a, b: test_utils.complex_cmp(b, a, '__le__'),
    '__rgt__': lambda a, b: test_utils.complex_cmp(b, a, '__gt__'),
    '__rge__': lambda a, b: test_utils.complex_cmp(b, a, '__ge__'),
}


def op_template(lhs, rhs, op: str):
    """Operation test template

    Args:
        lhs (any): Left hand side argument
        rhs (any): Right hand side argument
        op (str): Operation to perform (Python function)
    """

    rhs_float = isinstance(
        rhs,
        (
            float,
            complex,
            numpy.floating,
            numpy.complexfloating,
            mpmath.mpf,
            mpmath.mpc,
            pyfixed.mpfr_type,
            pyfixed.mpc_type
        )
    )
    op_assign = op.startswith('__i')
    float_result = not op_assign and not op in (
        '__eq__',
        '__ne__',
        '__gt__',
        '__ge__',
        '__lt__',
        '__le__',
        '__req__',
        '__rne__',
        '__rgt__',
        '__rge__',
        '__rlt__',
        '__rle__',
    ) and rhs_float

    def run_op():
        return test_utils.operation_executer(lhs, rhs, op)

    if op.startswith('__r') and \
            not 'shift' in op and \
            isinstance(rhs, pyfixed.ComplexFixed) and \
            hasattr(pyfixed.ComplexFixed, op):
        assert getattr(lhs, op)(rhs) is NotImplemented
        return

    # Note: rhs != 0 is performed because for whatever reason bool(gmpy2.mpc(0)) is True
    if 'div' in op and not (bool(lhs) if op.startswith('__r') else (rhs != 0)):
        if op_assign or not rhs_float:
            # Check how pyfixed handles division by 0
            test_utils.behavior_check('undefined', run_op)
        # else skip
        return

    # Calculate expected result
    conv_lhs = lhs.mpmath()
    # Convert to mpf
    if isinstance(rhs, (pyfixed.Fixed, pyfixed.ComplexFixed)):
        conv_rhs = rhs.mpmath()
    elif isinstance(rhs, (int, numpy.bool, numpy.integer, pyfixed.mpz_type)):
        conv_rhs = pyfixed.backend(rhs)
    elif isinstance(rhs, (float, complex, numpy.floating, numpy.complexfloating)):
        conv_rhs = mpmath.mpmathify(rhs)
    elif isinstance(rhs, pyfixed.mpfr_type):
        conv_rhs = pyfixed.mpfr_to_mpf(rhs)
    elif isinstance(rhs, pyfixed.mpc_type):
        conv_rhs = pyfixed.mpc_to_mpc(rhs)
    else:
        conv_rhs = rhs

    # Calculate the precise result, without fixed-point simulation
    if hasattr(conv_lhs, op) and not op in (
        '__lt__',
        '__le__',
        '__gt__',
        '__ge__'
    ):
        precise_expected = getattr(conv_lhs, op)(conv_rhs)
    else:
        precise_expected = OP_DICT[op](conv_lhs, conv_rhs)

    # Get the result and its type, as well as raised exceptions
    with pyfixed.with_partial_state(
            overflow_behavior=pyfixed.FixedBehavior.STICKY,
            underflow_behavior=pyfixed.FixedBehavior.STICKY,
            undefined_behavior=pyfixed.FixedBehavior.STICKY
    ):
        actual = run_op()
        of, uf, ud = pyfixed.get_sticky()

    assert actual is not NotImplemented

    if float_result:
        # Result should be float

        c_type = pyfixed.ComplexFixed._complex_type_helper(rhs)

        if pyfixed.mpfr_type is not float and isinstance(rhs, (pyfixed.mpfr_type, pyfixed.mpc_type)):
            def fixed_to_rhs(x):
                return x.mpc()
        else:
            fixed_to_rhs = c_type

        if not isinstance(rhs, (mpmath.mpf, mpmath.mpc)):
            # mpmath differs in the way it handles infinite values
            rhs_lhs = fixed_to_rhs(lhs)

            if 'div' in op:
                div = pyfixed.ComplexFixed._floordiv_helper(rhs, rhs_lhs)  \
                    if op.startswith('__r')                                \
                    else pyfixed.ComplexFixed._floordiv_helper(rhs_lhs, rhs)

            if 'floordiv' in op:
                precise_expected = div
            else:
                precise_expected = test_utils.operation_executer(rhs_lhs, rhs, op)

        def check_component(p_c, a_c):
            return p_c == a_c or (p_c != p_c and a_c != a_c)

        assert type(actual) == c_type
        assert check_component(precise_expected.real, actual.real) and \
            check_component(precise_expected.imag, actual.imag)

        return

    # Simulate fixed-point behavior
    def sim(x, a):
        epsilon = mpmath.ldexp(1, -a.fraction_bits)

        # Round like pyfixed
        result = test_utils.complex_ldexp(
            test_utils.rounding_modes[pyfixed.get_fixed_state().rounding](
                test_utils.complex_ldexp(
                    x,
                    a.fraction_bits
                )
            ),
            -a.fraction_bits
        )

        has_underflow = (
            (
                'div' in op and
                not op.startswith('__r') and
                mpmath.isinf(conv_rhs) and
                not mpmath.isnan(conv_rhs)
            ) or
            (
                (
                    'add' in op or
                    'sub' in op or
                    'mul' in op or
                    'div' in op and op.startswith('__r')
                ) and
                (
                    conv_rhs.real and abs(conv_rhs.real) < epsilon or
                    conv_rhs.imag and abs(conv_rhs.imag) < epsilon
                )
            ) or
            (x.real and abs(x.real) < epsilon) or
            (x.imag and abs(x.imag) < epsilon) or
            (result.real == 0 and x.real != 0) or
            (result.imag == 0 and x.imag != 0)
        )

        if a.saturation:
            # Saturate
            min_val = mpmath.ldexp(a._min_val, -a.fraction_bits)
            max_val = mpmath.ldexp(a._max_val, -a.fraction_bits)

            sat_result = mpmath.mpc(
                min(max(result.real, min_val), max_val),
                min(max(result.imag, min_val), max_val)
            )

            def check_of(r, s):
                return not mpmath.isnan(r) and r != s

            return (
                sat_result,
                has_underflow,
                (
                    'add' in op or
                    'sub' in op or
                    ('mul' in op and conv_lhs != 0) or
                    ('div' in op and isinstance(conv_rhs, mpmath.mpc))
                ) and mpmath.isinf(conv_rhs) or
                check_of(result.real, sat_result.real) or
                check_of(result.imag, sat_result.imag)
            )
        else:
            def overflow(v):
                if mpmath.isinf(v):
                    return a.mpmath() if op in ('__iadd__', '__isub__') else mpmath.mpf(0)

                limit = mpmath.ldexp(1, a.bits - a.fraction_bits)

                of = v % limit
                if a.sign and of >= limit / 2:
                    of -= limit

                return of

            return (
                mpmath.mpc(overflow(result.real), overflow(result.imag)),
                has_underflow,
                False
            )

    if not isinstance(precise_expected, bool):
        expected, has_underflow, has_overflow = sim(precise_expected, actual)
    else:
        expected = precise_expected
        has_underflow = False
        has_overflow = False

    if of or uf or ud:
        underflow_value = 0
        undefined_value = 0, 0

        error = []
        if of:
            error.append('overflow')
        if uf:
            error.append('underflow')
        if ud:
            error.append('undefined')

        half_epsilon = mpmath.ldexp(1, -lhs.fraction_bits - 1)
        twice_max = mpmath.ldexp(1, 2 * lhs.integer_bits)

        assert ud or of == has_overflow
        assert (
            uf == has_underflow or
            has_overflow and not uf or
            (
                not 'r' in op and
                not 'div' in op and
                has_underflow and
                (
                    conv_rhs.real and
                    abs(conv_rhs.real) < half_epsilon or
                    conv_rhs.imag and
                    abs(conv_rhs.imag) < half_epsilon
                )
            )
            or
            (
                not 'div' in op and
                has_underflow and
                (
                    abs(conv_rhs.real) > twice_max or
                    abs(conv_rhs.imag) > twice_max
                )
            )
        )

        expected_fixed = (
            mpmath.ldexp(expected.real, actual.fraction_bits),
            mpmath.ldexp(expected.imag, actual.fraction_bits)
        )

        if ud:
            # Remove NaNs
            assert not mpmath.isfinite(precise_expected)
            expected_fixed = *(
                0 if mpmath.isnan(v) else v
                for v in expected_fixed
            ),
            expected = mpmath.mpc(
                *(
                    0 if mpmath.isnan(v) else v
                    for v in (expected.real, expected.imag)
                )
            )
            undefined_value = expected_fixed

        if uf:
            underflow_value = expected_fixed

        test_utils.behavior_check(
            error,
            run_op,
            underflow_value=underflow_value,
            undefined_value=undefined_value
        )

    # Extract internal value and convert for comparison
    if not isinstance(expected, bool):
        actual = actual.mpmath()

    # Compare
    assert expected == actual


class ArithmeticsTestSuite(test_utils.TestSuite):
    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)

        self.workprec = max(
            2 * self.precision,
            # mpmath rounds to even internally, so to avoid that we need to
            # be able to represent every possible input with exact precision
            int(
                numpy.finfo(numpy.float128).maxexp -
                numpy.log2(numpy.finfo(numpy.float128).smallest_subnormal)
            )
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
            # Saturated
            (
                test_utils.fixed_range,
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                True
            ),
            (
                test_utils.fixed_range,
                self.bits,
                self.bits,
                True,
                True
            ),
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
            # Complex saturated
            (
                test_utils.complex_range,
                test_utils.fixed_range,
                pyfixed.ComplexFixed,
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                True
            ),
            (
                test_utils.complex_range,
                test_utils.fixed_range,
                pyfixed.ComplexFixed,
                self.bits,
                self.bits,
                True,
                True
            ),
            (
                test_utils.complex_range,
                test_utils.fixed_range,
                pyfixed.ComplexFixed,
                self.fraction_bits // 2,
                self.integer_bits // 2,
                True,
                True
            ),
            # Complex unsaturated
            (
                test_utils.complex_range,
                test_utils.fixed_range,
                pyfixed.ComplexFixed,
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                False
            ),
            (
                test_utils.complex_range,
                test_utils.fixed_range,
                pyfixed.ComplexFixed,
                self.bits,
                self.bits,
                True,
                False
            ),
            (
                test_utils.complex_range,
                test_utils.fixed_range,
                pyfixed.ComplexFixed,
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

        self.assign_ranges = self.int_ranges + test_utils.FLOAT_RANGES
        self.ranges = self.assign_ranges + test_utils.COMPLEX_RANGES

        shift_range = (-2 * self.bits, 2 * (self.bits + 1))       \
            if test_utils.TEST_INT_RANGE_SAMPLES == 0 \
            else tuple()
        self.shift_ranges = (
            (test_utils.iterator, False, True),
            (test_utils.iterator, numpy.bool(False), numpy.bool(True)),
            (test_utils.int_range, int, *shift_range),
            (test_utils.int_range, numpy.int64, *shift_range),
            (test_utils.int_range, numpy.uint64, *shift_range),
            (test_utils.int_range, pyfixed.mpz_type, *shift_range)
            if pyfixed.mpz_type is not int
            else None,
        )

        self.tests = (
            *(
                (
                    self.test_op,
                    mode,
                    op,
                    rhs
                )
                for rhs in self.assign_ranges
                for mode in pyfixed.FixedRounding
                for op in (
                    '__iadd__',
                    '__isub__',
                    '__imul__',
                    '__itruediv__',
                    '__ifloordiv__',
                )
            ),
            *(
                (
                    self.test_op,
                    mode,
                    op,
                    rhs
                )
                for rhs in self.ranges
                for mode in pyfixed.FixedRounding
                for op in (
                    '__add__',
                    '__radd__',
                    '__sub__',
                    '__rsub__',
                    '__mul__',
                    '__rmul__',
                    '__truediv__',
                    '__rtruediv__',
                    '__floordiv__',
                    '__rfloordiv__',
                )
            ),
            *(
                (
                    self.test_op,
                    None,  # No rounding is performed
                    op,
                    rhs
                )
                for rhs in self.ranges
                for op in (
                    '__eq__',
                    '__ne__',
                    '__lt__',
                    '__le__',
                    '__gt__',
                    '__ge__',
                )
            ),
            *(
                (
                    self.test_op,
                    None,  # No rounding is performed
                    op,
                    rhs
                )
                for rhs in self.int_ranges +
                test_utils.NUMPY_FLOAT_RANGES +
                test_utils.NUMPY_COMPLEX_RANGES +
                test_utils.MPMATH_FLOAT_RANGES +
                test_utils.MPMATH_COMPLEX_RANGES +
                test_utils.GMPY2_FLOAT_RANGES
                for op in (
                    '__req__',
                    '__rne__',
                )
            ),
            *(
                (
                    self.test_op,
                    None,  # No rounding is performed
                    op,
                    rhs
                )
                for rhs in self.int_ranges +
                test_utils.NUMPY_FLOAT_RANGES +
                test_utils.NUMPY_COMPLEX_RANGES
                for op in (
                    '__rlt__',
                    '__rle__',
                    '__rgt__',
                    '__rge__',
                )
            ),
            *(
                (
                    self.test_op,
                    mode,
                    op,
                    rhs
                )
                for rhs in self.shift_ranges
                for mode in pyfixed.FixedRounding
                for op in (
                    '__ilshift__',
                    '__lshift__',
                    '__irshift__',
                    '__rshift__',
                )
            ),
            *(
                (
                    self.test_undefined,
                    op,
                    rhs
                )
                for rhs in (
                    complex,
                    numpy.complex64,
                    numpy.complex128,
                    numpy.complex256,
                    mpmath.mpc,
                    pyfixed.mpc_type,
                )
                for op in (
                    '__iadd__',
                    '__isub__',
                    '__imul__',
                    '__itruediv__',
                    '__ifloordiv__',
                )
            ),
            *(
                (
                    self.test_not_implemented,
                    op,
                    rhs
                )
                for rhs in (
                    float,
                    numpy.float32,
                    numpy.float64,
                    numpy.float128,
                    mpmath.mpf,
                    pyfixed.mpc_type,
                    complex,
                    numpy.complex64,
                    numpy.complex128,
                    numpy.complex256,
                    mpmath.mpc,
                    pyfixed.mpc_type,
                )
                for op in (
                    '__ilshift__',
                    '__lshift__',
                    '__irshift__',
                    '__rshift__',
                )
            ),
        )

    def test_op(
            self,
            mode: pyfixed.FixedRounding,
            op: str,
            rhs: tuple | list
    ):
        """Tests a single operation under a certain configuration

        Args:
            mode (pyfixed.FixedRounding): Rounding mode
            op (str): Operation to test
            rhs (tuple, list): RHS function and its arguments
        """

        if rhs is None:
            return

        with mpmath.workprec(self.workprec), pyfixed.with_partial_state(rounding=mode):
            for lhs in test_utils.complex_range(
                test_utils.fixed_range,
                pyfixed.ComplexFixed,
                self.fraction_bits,
                self.integer_bits,
                self.sign,
                self.saturation
            ):
                for val in rhs[0](*(rhs[1:])):
                    op_template(lhs, val, op)

    def test_undefined(self, op: str, rhs: type):
        """Tests a single operation with an unsupported
           data type to see if it raises FixedUndefined

        Args:
            op (str): Operation to test
            rhs (type): Unsupported type to test
        """

        with pytest.raises(pyfixed.FixedUndefined):
            test_utils.operation_executer(
                pyfixed.ComplexFixed(
                    fraction_bits=self.fraction_bits,
                    integer_bits=self.integer_bits,
                    sign=self.sign,
                    saturation=self.saturation
                ),
                rhs(0),
                op
            )

    def test_not_implemented(self, op: str, rhs: type):
        """Tests a single operation with an unsupported
           data type to see if it returns NotImplemented

        Args:
            op (str): Operation to test
            rhs (type): Unsupported type to test
        """

        with pytest.raises(TypeError):
            assert test_utils.operation_executer(
                pyfixed.ComplexFixed(
                    fraction_bits=self.fraction_bits,
                    integer_bits=self.integer_bits,
                    sign=self.sign,
                    saturation=self.saturation
                ),
                rhs(0),
                op
            ) is NotImplemented


test = test_utils.run_tests(ArithmeticsTestSuite)
