# SPDX-FileCopyrightText: 2025 Florian Obersteiner / KIT
# SPDX-FileContributor: Florian Obersteiner <f.obersteiner@kit.edu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Helpers to format plots."""

import numpy as np

###############################################################################


def get_plot_range(
    v: list | np.ndarray | np.ma.masked_array,
    add_percent: float = 5,
    v_min_lim: float | None = None,
    v_max_lim: float | None = None,
    xrange: list[float] | None = None,
    x: list | np.ndarray | None = None,
) -> tuple[float, float]:
    """
    Adjust y-axis range of matplotlib pyplot for a given vector v.

    Parameters
    ----------
    v : list or numpy 1d array
        dependent variable.
    add_percent : numeric type scalar value, optional
        percent of the range of v that should be added to result. The default is 5.
    v_min_lim : numeric type scalar value, optional
        minimum value for lower yrange limit. The default is None.
    v_max_lim : numeric type scalar value, optional
        maximum value for upper yrange limit. The default is None.
    xrange : list, optional
        [lower_limit, upper_limit] of independent variable. The default is None.
    x : list or numpy 1d array, optional
        independent variable. The default is None.

    Returns
    -------
    result : tuple, 2 elements
        lower and upper limit.

    """
    if isinstance(v, np.ma.masked_array):
        v = v[~v.mask]

    if not isinstance(v, np.ndarray):
        v = np.array(v)  # ensure array type

    if x is not None and xrange is not None:
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        x = np.sort(x)  # monotonically increasing x-vector (e.g. time)
        if len(x) == len(v):
            w_xvd = (x >= xrange[0]) & (x <= xrange[1])  # type: ignore
            v = v[w_xvd]

    v = v[np.isfinite(v)]

    if len(v) < 2:
        # it is better not to raise an exception in case no valid input,
        # to avoid errors further down...
        return (-1.0, 1.0)

    v_min, v_max = np.min(v), np.max(v)
    offset = (abs(v_min) + abs(v_max)) / 2 * add_percent / 100
    result = [v_min - offset, v_max + offset]

    if v_min_lim and result[0] < v_min_lim:
        result[0] = v_min_lim

    if v_max_lim and result[1] > v_max_lim:
        result[1] = v_max_lim

    return tuple(result)


###############################################################################


def nticks_yrange(
    yrange: list[float], nticks: int, range_as_multiple_of: int = 10
) -> tuple[float, float]:
    """
    Update a plot yrange so that it fits nicely with a certain number of ticks.

    Parameters
    ----------
    yrange : 2-element tuple or list
        the yrange to modify.
    nticks : int
        number of ticks along y-axis.
    range_as_multiples_of: int, optional
        make the yrange divisible w/o remainder by .... The default is 10.

    Returns
    -------
    result : 2-element tuple
        updated yrange.

    Examples
    --------
    >>> nticks_yrange([12, 47], nticks=5, range_as_multiple_of=10)
    (10.0, 50.0)
    >>> # Explanation:
    >>> # - Input range [12, 47] is first rounded to [10, 50] to be divisible by 10
    >>> # - With nticks=5, we need 4 equal intervals (nticks-1)
    >>> # - The range 40 is divisible by both 4 and 10, so the result is (10.0, 50.0)

    >>> nticks_yrange([12, 47], nticks=6, range_as_multiple_of=5)
    (10.0, 50.0)
    >>> # Explanation:
    >>> # - Input range [12, 47] is rounded to [10, 50] to be divisible by 5
    >>> # - With nticks=6, we need 5 equal intervals (nticks-1)
    >>> # - The range 40 is divisible 5, so the result is (10.0, 50.0)

    >>> nticks_yrange([-3, 22], nticks=7, range_as_multiple_of=10)
    (-10.0, 50.0)
    >>> # Explanation:
    >>> # - Input range [-3, 22] is rounded to [-10, 30] to be divisible by 10
    >>> # - With nticks=7, we need 6 equal intervals (nticks-1)
    >>> # - The LCM of 6 and 10 is 30, so the range needs to be a multiple of 30
    >>> # - The range is expanded to 60 (2 × 30), resulting in (-10.0, 50.0)
    """
    lower = np.floor(yrange[0] / range_as_multiple_of) * range_as_multiple_of
    upper = np.ceil(yrange[1] / range_as_multiple_of) * range_as_multiple_of

    # Calculate the range needed to be divisible by both nticks-1 and range_as_multiple_of
    range_needed = np.lcm(nticks - 1, range_as_multiple_of)

    # Calculate how many complete range_needed units fit in our current range
    current_range = upper - lower
    num_units = int(np.ceil(current_range / range_needed))

    # Adjust the upper bound to make the range divisible by both factors
    upper = lower + num_units * range_needed

    return (float(lower), float(upper))


###############################################################################


if __name__ == "__main__":
    import doctest

    doctest.testmod()
