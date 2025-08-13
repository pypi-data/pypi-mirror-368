=====
Usage
=====

Converting to Other Types
------------------------------

:py:mod:`!pyfixed` supports conversion to and from the following types:

- :py:class:`!bool`
- :py:class:`!int`
- :py:class:`!float`
- :py:class:`!complex`
- :py:class:`!numpy.integer`
- :py:class:`!numpy.floating`
- :py:class:`!numpy.complexfloating`
- :py:class:`!mpmath.mpf`
- :py:class:`!mpmath.mpc`
- :py:class:`!gmpy2.mpz`
- :py:class:`!gmpy2.mpfr`
- :py:class:`!gmpy2.mpc`

:py:class:`!pyfixed.Fixed` and :py:class:`!pyfixed.ComplexFixed` support conversion
from these types by simply passing them to the :py:meth:`!__init__` function, e.g.:

::

  pyfixed.Fixed(1)
  pyfixed.Fixed(numpy.single(...))
  pyfixed.ComplexFixed(1j)
  ...

Python and NumPy
================

Converting to native Python types and NumPy is done via the conventional methods:

::

  complex(pyfixed.ComplexFixed(...))
  numpy.single(pyfixed.Fixed(...))
  ...


:py:mod:`!mpmath`
=================

:py:class:`!pyfixed.Fixed` supports native conversion to :py:class:`!mpmath.mpf` via the :py:meth:`!_mpf_` method, for example:

::

  mpmath.mpf(pyfixed.Fixed(...))
  mpmath.expjpi(2 * pyfixed.Fixed(...))
  ...

However, :py:class:`!pyfixed.ComplexFixed` doesn't provide a native conversion, since :py:mod:`!mpmath` sometimes
references the complex type instead of casting to :py:class:`!mpmath.mpc`, resulting in bad typing.

Both :py:class:`!pyfixed.Fixed` and :py:class:`!pyfixed.ComplexFixed` provide the :py:meth:`!mpmath()`
method, which converts to :py:class:`!mpmath.mpf` and :py:class:`!mpmath.mpc`, accordingly.

:py:mod:`!gmpy2`
================

Both :py:class:`!pyfixed.Fixed` and :py:class:`!pyfixed.ComplexFixed` can be converted to
:py:mod:`!gmpy2` types using the method with the type's name.
Native support isn't provided because it causes :py:mod:`!gmpy2` to convert to :py:class:`!gmpy2.mpfr`
when performing reverse operations involving :py:class:`!pyfixed.Fixed` and :py:class:`!gmpy2.mpz`
(e.g. ``gmpy2.mpz(1) + pyfixed.Fixed(1)`` results in ``gmpy2.mpfr(2)`` instead of ``pyfixed.Fixed(2)``).

:py:mod:`!gmpy2` Backend
------------------------

:py:mod:`!pyfixed` supports two integer backends: Python's :py:obj:`!int` and :py:class:`!gmpy2.mpz`.

| When available, :py:mod:`!pyfixed` will use :py:class:`!gmpy2.mpz` to improve performance.
| This can be disabled by setting the environment variable ``PYFIXED_NOGMPY`` to be non-zero.

Additionally, :py:mod:`!pyfixed` will use :py:class:`!gmpy2.mpz` only if :py:mod:`!mpmath` uses it.

:py:class:`!pyfixed.Fixed` and :py:class:`!pyfixed.ComplexFixed` can be converted to and from :py:class:`!gmpy2.mpz`,
:py:class:`!gmpy2.mpfr` and :py:class:`!gmpy2.mpc`, and support arithmetics involving them.

Problems with :py:class:`!gmpy2.mpz`
====================================

Sometimes, :py:class:`!gmpy2.mpz` can "infect" types and convert them to itself.
This is problematic when code explicitly requires :py:obj:`!int`.

One such occurrence is in the integration of :py:class:`!gmpy2` in :py:mod:`!mpmath`.
:py:mod:`!mpmath` passes a precision to the function :py:func:`!gmpy2._normalize`, only accepts an :py:obj:`!int` precision.
However, :py:class:`!gmpy2.mpz` can be injected into that argument by directly modifying the exponent
of :py:class:`!mpmath.mpf`, e.g. via :py:func:`!mpmath.ldexp`.
This can sometimes lead to an exception, since :py:mod:`!mpmath` will calculate the precision using
:py:class:`!gmpy2.mpz` instead of :py:obj:`!int`, then pass it to :py:func:`!gmpy2._normalize`, resulting in an exception.

Example for this behavior:

::

  mpmath.floor(mpmath.ldexp(gmpy2.mpfr(1.5), gmpy2.mpz(0)))

Besides that, :py:mod:`!gmpy2` has some memory leaks, which affect the implementation of :py:mod:`!pyfixed`.

Aliases
-------

:py:class:`!pyfixed.Fixed` and :py:class:`!pyfixed.ComplexFixed` are used for all fixed-point configurations.
:py:class:`!pyfixed` provides aliases, which are configuration-specific types.

Aliases can be created using a configuration, or from an existing fixed-point object.

Returned Types
--------------

:py:mod:`!pyfixed` differs between in-place binary operations (e.g. ``a += b``) and out-of-place binary operations (e.g. ``a + b``).

In-place operations are performed in the highest precision possible, and always return the
LHS' type (e.g. ``pyfixed.Fixed() += float()`` will return :py:class:`!pyfixed.Fixed`).
This makes some operations involving floats impossible to perform without dynamic precision (or very high static precision).

Out-of-place operations return the more precise type and convert both operands to it, with fixed-point being more
precise than integral types (:py:class:`!bool` and integers), and floating-point being more precise than fixed-point.
These operations allow for any float operand, but are less precise due to conversion losses.

Comparisons are the only fully lossless out-of-place binary operations. They're performed in the highest precision without casting.

Out-of-place operations involving an integral operand are guaranteed to be as precise as in-place operations (because they use them).

Out-of-place operations involving only fixed-point operands use a combined precision, which uses the max. bits from each fixed-point
configuration (e.g. ``fraction_bits=16, integer_bits=15, sign=True, saturation=True`` for
``fraction_bits=16, integer_bits=0, sign=True, saturation=False`` and
``fraction_bits=8, integer_bits=15, sign=False, saturation=True``).

Out-of-place operations involving a floating-point operand simply cast to float and then calculate.
That means :py:mod:`!pyfixed`'s configuration doesn't affect them.

As for unary operations, they all return the original type, except for rounding functions (:py:func:`!floor`,
:py:func:`!ceil`, :py:func:`!trunc` and :py:func:`!round`), which round to integers, and return :py:obj:`!pyfixed.backend`
(except for :py:func:`!round` with a ``ndigits`` argument).

Some operations on floats are not supported since they operate on very high bit widths.
Such operations are :py:meth:`!pyfixed.Fixed.divmod` and in-place operations on :py:class:`pyfixed.ComplexFixed`.

.. note::
  Instead of returning :py:obj:`!NotImplemented`, :py:class:`!pyfixed.ComplexFixed`'s in-place operators
  raise the undefined exception. This is done to avoid Python implementing the operators as

  ::

    def __iadd__(self, other):
      return self + other

Saturation
----------

:py:mod:`!pyfixed` supports saturated and unsaturated fixed-point numbers.

When a value is written to a fixed-point number, the internal method :py:meth:`!pyfixed.Fixed._set`
checks if the value fits within the number's bit-width.

A saturated number will "clip" the value, so that it doesn't go outside the representable range.
For example, ``pyfixed.q15(1)`` will result in ``0.999969482421875``, since ``1`` is
just outside the representable range.

Contrary, an unsaturated number will simulate overflow (as Python integers expand instead).
For example, ``pyfixed.Fixed(1, fraction_bits=15, integer_bits=0, sign=True, saturation=True)``
will result in ``-1``, since the value ``1`` (internal value ``32768``) overflows.

Rounding Modes
--------------

:py:mod:`!pyfixed` offers 10 rounding modes, as described in :py:class:`pyfixed.fixed.FixedRounding`.

Each rounding mode can be used for regular arithmetics and for :py:meth:`pyfixed.fixed.Fixed.divmod`.

Some functions perform explicit rounding:

- :py:func:`!floor`, :py:func:`!ceil` and :py:func:`!trunc`: round in the specified mode,
  regardless of the current rounding mode.
- :py:func:`!round`: round to integer according to the current rounding mode.
  Note that ``ndigits`` is in base 2, unlike Python's base 10.
- :py:meth:`floordiv` (``//``): divide and floor the result, regardless of the current rounding mode.
  The result is returned as fixed-point.
- :py:meth:`mod` (``%``): divide and return the remainder.
  Conforms to Python's rounding (flooring).
- :py:func:`divmod`: divide and return a rounded result and a remainder.
  Conforms to Python's rounding (flooring).
- :py:meth:`!pyfixed.fixed.Fixed.divmod`: divide and return a rounded result and a remainder.
  Only :py:class:`!pyfixed.fixed.Fixed` and integer types are allowed.
  The rounding mode is given as an argument.

.. note::

  Out-of-place operations involving floats round according to the floating-point backend.

Comparisons
-----------

Unlike C and NumPy comparisons, and similar to Python and mpmath, :py:mod:`!pyfixed` performs accurate comparisons without casting/converting between types.

| For example, ``numpy.float32(2 ** 25) == 2 ** 25 - 1`` is true, even though the numbers are different.
| That's because C and NumPy convert the integer to :py:class:`!float32`.

Another key difference is complex comparisons - :py:mod:`!pyfixed` allows for ordered comparisons when two components are equal.

| For example, ``pyfixed.ComplexFixed(1 + 1j)`` is greater than ``pyfixed.ComplexFixed(1 - 1j)``, since the real components are equal, and ``1j`` is greater than ``-1j``;
| ``pyfixed.ComplexFixed(1 + 1j)`` is less than ``pyfixed.ComplexFixed(2 + 1j)``, since the imaginary components are equal, and ``1`` is less than ``2``.

However, comparing ``pyfixed.ComplexFixed(1 + 1j)`` and ``pyfixed.ComplexFixed(2 - 1j)`` is unordered, since they don't share a common axis to compare on.

Both :py:class:`!pyfixed.Fixed` and :py:class:`!pyfixed.ComplexFixed` provide the :py:meth:`!cmp` method, which returns the ordering of the compared numbers.

Utility
-------

:py:mod:`!pyfixed` provides utility functions, some of which are similar to C functions:

- :py:func:`pyfixed.fixed.sign`
- :py:func:`pyfixed.fixed.copysign`
- :py:func:`pyfixed.fixed.nextafter`
- :py:func:`pyfixed.fixed.ilogb`
- :py:func:`pyfixed.fixed.frexp`
- :py:func:`pyfixed.fixed.modf`

Exceptions and Sticky Flags
---------------------------

| :py:mod:`!pyfixed` supports numeric error exceptions.
| These exceptions are raised when a mathematical error occurs (e.g. division by 0), or when :py:mod:`!pyfixed` can't correctly represent a value (e.g. overflow).
| All exceptions can be disabled (i.e. ignored).

| :py:mod:`!pyfixed` also offers sticky flags, which are silent exceptions - they aren't raised, but rather set a flag, which can later be read by the user.
| Note that the sticky flags are only cleared when modifying the current state, or via :py:func:`pyfixed.fixed.get_sticky`.

There are some special cases regarding exceptions:

- :py:meth:`!cmp` performs a lossless comparison, so it won't raise overflow or underflow, and it handles undefined scenarios by returning unordered.
- All rounding functions: never raise overflow, underflow and undefined, as they round a valid value and return an integer.
  :py:func:`!round` might raise overflow when ``ndigits`` is given.
- :py:meth:`!__floordiv__`, :py:meth:`__mod__` and :py:func:`!divmod` never raise underflow, as the result is floored.
