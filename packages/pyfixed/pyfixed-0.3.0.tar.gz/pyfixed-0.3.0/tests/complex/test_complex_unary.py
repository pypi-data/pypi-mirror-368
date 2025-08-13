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

"""Tests unary operators (e.g. -ComplexFixed etc.)
"""

import pyfixed
import pyfixed.test_utils as test_utils


class UnaryTestSuite(test_utils.TestSuite):
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
            self.test_plus,
            self.test_minus,
        )

    def test_plus(self):
        for value in self._range():
            plus = +value
            assert value.real == plus.real
            assert value.imag == plus.imag

    def test_minus(self):
        for value in self._range():
            try:
                minus = -value
                assert -value.real == minus.real
                assert -value.imag == minus.imag
            except pyfixed.FixedOverflow:
                with pyfixed.with_partial_state(overflow_behavior=pyfixed.FixedBehavior.IGNORE):
                    minus = -value
                    assert (
                        not self.sign
                        or minus.real.value == minus.real._max_val
                        or minus.imag.value == minus.imag._max_val
                    )


test = test_utils.run_tests(UnaryTestSuite)
