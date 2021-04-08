"""Meshing."""


import numpy as np


def split_grid(a):
    """

    Examples
    --------
    >>> import numpy as np
    >>> a = np.arange(1, 5)
    >>> print(a)
    [1 2 3 4]
    >>> b = split_grid(a)
    >>> print(np.round(b, 1))
    [1.  1.3 1.7 2.  2.3 2.7 3.  3.3 3.7 4. ]
    """

    diff = np.diff(a)
    x = a[:-1] + diff * 1.0 / 3.0
    y = a[:-1] + diff * 2.0 / 3.0
    full = np.append(np.append(a, x), y)
    return np.sort(full)


def new_grid(a):
    diff = np.diff(a)
    x = a[:-1] + diff * 1.0 / 3.0
    y = a[:-1] + diff * 2.0 / 3.0
    full = np.append(x, y)
    return np.sort(full)


def insert_two_points(a):
    diff = np.diff(a)
    x = a[:-1] + diff * 1.0 / 3.0
    y = a[:-1] + diff * 2.0 / 3.0
    full = np.append(x, y)
    return np.sort(full), np.repeat(diff, 2)


def insert_three_points(a):
    diff = np.diff(a)
    x = a[:-1] + diff * 1.0 / 5.0
    y = a[:-1] + diff * 2.0 / 5.0
    z = a[:-1] + diff * 3.0 / 5.0
    w = a[:-1] + diff * 4.0 / 5.0
    full = np.append(x, y)
    full2 = np.append(full, z)
    full3 = np.append(full2, w)
    return np.sort(full3), np.repeat(diff, 4)


def new_grid2(a):
    diff = np.diff(a)
    x = a[:-1] + diff * 1.0 / 2.0
    return np.sort(x)


def insert_single_points(a):
    diff = np.diff(a)
    x = a[:-1] + diff * 1.0 / 2.0
    return np.sort(x), diff
