#!/usr/bin/env python

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

"""fixed_cmp - Visually compares fixed-point to floating point
"""

import argparse
import math
from matplotlib import pyplot
import numpy


def plot_fixed_exps(f: int, i: int):
    """Plots the exponent precision graph for fixed-point

    Args:
        f (int): Fraction bits
        i (int): Integer bits
    """

    exps = [i for i in range(-f, i)]
    pyplot.plot(
        [v for exp in exps for v in (exp, exp + 1)],
        [
            v
            for bits, _ in enumerate(exps)
            for v in (bits + 1,) * 2
        ]
    )


def plot_float_exps(dtype: numpy.dtype):
    """Plots the exponent precision graph for floating point

    Args:
        dtype (numpy.dtype): Floating point type to plot for
    """

    finfo = numpy.finfo(dtype)
    exps = range(finfo.minexp, finfo.maxexp + 1)
    nmant = finfo.nmant + 1
    pyplot.plot(
        # Subnormal values
        [
            v
            for exp in range(-nmant, 0)
            for v in (finfo.minexp + exp, finfo.minexp + exp + 1)
        ] +
        # Normal values
        [v for exp in exps for v in (exp, exp + 1)],
        # Subnormal values
        [v for bits in range(nmant) for v in (bits + 1, ) * 2] +
        # Normal values
        [nmant] * (2 * len(exps))
    )


def plot_posit_exps(n: int):
    """Plots the exponent precision graph for posits

    Args:
        n (int): Posit width
    """
    # Create pairs of exponents and fraction bits and sort them
    vals = sorted(
        zip(
            [
                (1 - 2 * s) * (4 * r_val + e + s)
                # Sign bit (positive, negative)
                for s in (0, 1)
                # Regime bits (including last)
                for r in range(2, n)
                # Exponent
                for e in (range(0, math.ceil(2 ** min(n - 1 - r, 2))))
                # Regime value (minus (r < n - 1) to ignore the last bit, if present)
                for r_val in (-(r - (r < n - 1)), r - 1 - (r < n - 1))
            ],
            [
                # +1 because there's the implicit 1 bit
                1 + max(0, n - 1 - r - 2)
                for _ in (None, None)
                for r in range(2, n)
                for _ in (range(0, math.ceil(2 ** min(n - 1 - r, 2))))
                for _ in (None, None)
            ]
        )
    )
    pyplot.plot(
        [v for val in vals for v in [val[0], val[0] + 1]],
        [v for val in vals for v in [val[1]] * 2]
    )


def plot_interval(N: int, M: int, iters: int):
    """Plots an exponent interval

    Args:
        N (int): Interval start
        M (int): Interval end
        iters (int): Number of iterations (i.e. number of arithmetic operations number)

    Raises:
        ValueError: Invalid interval parameters
    """

    if N >= 0 or M < 0:
        raise ValueError()

    for _ in range(iters):
        pyplot.plot((N, M), (M - N,) * 2)
        old_N = N
        N = min(2 * N, N - M)
        M = max(2 * M, M - old_N)


def main():
    'Main function'
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-fl',
        '--float',
        type=str,
        choices=('float16', 'float32', 'float64', 'float128'),
        nargs='*',
        help='Floating point type to compare with'
    )
    parser.add_argument(
        '-fi',
        '--fixed',
        type=str,
        nargs='*',
        help='Fixed-point formats, excluding the sign bit (e.g. 0.15 for Q15, 16.15 for Q17.15)'
    )
    parser.add_argument(
        '-p',
        '--posit',
        type=int,
        nargs='*',
        help='Posit widths'
    )
    parser.add_argument(
        '-i',
        '--interval',
        type=int,
        nargs=3,
        help='Interval parameters. '
        '1st and 2nd are the interval exponent limits, '
        '3rd is the number of iterations.'
    )

    args = parser.parse_args()

    if args.fixed:
        for f in args.fixed:
            int_bits, fract_bits = f.split('.')
            plot_fixed_exps(int(fract_bits), int(int_bits))

    if args.float:
        for f in args.float:
            plot_float_exps(numpy.__dict__[f])

    if args.posit:
        for n in args.posit:
            plot_posit_exps(n)

    if args.interval:
        plot_interval(*(args.interval))

    pyplot.show()


if __name__ == '__main__':
    exit(main())
