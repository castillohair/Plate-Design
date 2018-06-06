"""
Auxiliary math functions for platedesign.

"""

import numpy

def _ceil_log(x, r=1):
    """
    Return the ceiling of the input at a specified order of magnitude.

    If ``x = a*10^b``, where ``10**(r-1) <= a < 10**r``, then this function
    returns ``ceil(a)*10^b``, where ``ceil()`` is a standard ceiling
    function.

    Parameters
    ----------
    x : float or array
        Number to round.
    r : float or array
        Relative order of magnitude at which to round. See examples for
        more information.

    Returns
    -------
    float
        The log ceiling of `x`.

    Examples
    --------

    >>> _ceil_log(932)
    1000.0

    >>> _ceil_log(932, 2)
    940.0

    >>> _ceil_log(932, 3)
    932.0

    >>> _ceil_log(70)
    70.0

    >>> _ceil_log(71)
    80.0

    >>> _ceil_log(69.1)
    70.0

    >>> _ceil_log(6.9)
    7.0

    >>> _ceil_log(9.9)
    10.0

    >>> _ceil_log(numpy.array([34, 67, 5.6]))
    array([ 40.,  70.,   6.])

    >>> _ceil_log(numpy.array([34, 67, 5.6]), 2)
    array([ 34.,  67.,   5.6])

    >>> _ceil_log(numpy.array([34, 67, 5.6]), numpy.array([1, 2, 2]))
    array([ 40.,  67.,   5.6])

    """
    # xb is 10**b
    # When ``x = a1*10^b1`` and ``1 <= a1 < 10``, ``b1 = floor(log10(x))``.
    # ``a2 = 10*a1`` and ``b2 = b1 - 1``. By induction, ``b = b1 - (r - 1)``.
    xb = 10.**(numpy.floor(numpy.log10(x)) - (r-1))
    return numpy.ceil(x/xb) * xb