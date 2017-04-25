"""
Auxiliary math functions for platedesign.

"""

import numpy

def _ceil_log(x):
    """
    Return the ceiling of the input at the corresponding order of magnitude.

    If ``x = a*10^b``, where ``1 <= a < 10``, then this function returns
    ``ceil(a)*10^b``, where ``ceil()`` is a standard ceiling function.

    Parameters
    ----------
    x : float or array
        Number to round.

    Returns
    -------
    float
        The log ceiling of `x`.

    Examples
    --------

    >>> _ceil_log(932)
    1000.0

    >>> _ceil_log(70)
    70.0

    >>> _ceil_log(71)
    80.0

    >>> _ceil_log(69)
    70.0

    >>> _ceil_log(6.9)
    7.0

    >>> _ceil_log(9.9)
    10.0

    >>> _ceil_log(numpy.array([34, 67, 5.6]))
    array([ 40.,  70.,   6.])

    """
    xom = 10.**numpy.floor(numpy.log10(x))
    return numpy.ceil(x/xom)*xom