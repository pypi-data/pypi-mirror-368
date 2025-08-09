import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brenth


def min_tc_chord(chord, t):
    """Corrects the chord to maintain monotonic decreasing t/c at the tip.

    Parameters
    ----------
    chord : np.ndarray
        chord distribution
    t : np.ndarray
        blade absolute thickness distribution

    Returns
    -------
    np.ndarray
        chord distribution corrected monotonic decreasing t/c
    """
    tc = t / chord
    i_tc_min = np.argmin(tc)
    tc[i_tc_min:] = tc[i_tc_min]
    return t / tc


def root_chord(r, chord, chord_root, chord_max):
    """Makes a smooth chord that satisfies a given root chord and
    maximum chord from a ideal aerodynamic design

    Parameters
    ----------
    r : np.ndarray
        Span locations related to the chord [m]
    chord : np.ndarray
        Chord from an ideal aerodynamic design [m]
    chord_root : float
        Chord at the root of the blade (assumed to be at r[0]) [m]
    chord_max : float
        Maximum chord size [m]

    Returns
    -------
    chord_smooth: np.ndarray
        Chord that satisfy the chord constraints at the root and maximum
    """
    # Interpolation of chord
    chord_interp = PchipInterpolator(r, chord)

    # Find index closest to max chord
    i_cmax = np.argmin(abs(chord - chord_max))

    # Radius at the root
    r_root = r[0]

    # lower bound
    r0 = r[i_cmax]
    for i in range(i_cmax, 0, -1):
        if _r_start_obj(r0, chord_interp, r_root, chord_root, chord_max) > 0.0:
            break
        r0 = r[i]

    # Upper bound
    r1 = r[-1]
    for i in range(len(r) - 1, i_cmax, -1):
        if _r_start_obj(r1, chord_interp, r_root, chord_root, chord_max) < 0.0:
            break
        r1 = r[i]

    # Create smooth chord
    r_start, chord_poly = _get_chord_poly(
        chord_interp, r_root, chord_root, chord_max, [r0, r1]
    )

    # Create output chord
    chord_out = chord.copy()
    loc = r <= r_start
    chord_out[loc] = chord_poly(r[loc])
    return chord_out


def _get_chord_poly(chord_interp, r_root, c_root, c_max, r_range):
    # Get r_start
    r_start = _find_r_start(chord_interp, r_root, c_root, c_max, r_range)

    # Get poly
    chord_poly = _get_poly(
        r_root, c_root, r_start, chord_interp(r_start), chord_interp(r_start, 1)
    )
    return r_start, chord_poly


def _find_r_start(chord_interp, r_root, c_root, c_max, r_range):
    # Solve for r_start
    return brenth(_r_start_obj, *r_range, args=(chord_interp, r_root, c_root, c_max))


def _r_start_obj(r_start, chord_interp, r_root, c_root, c_max):
    # Get poly
    poly = _get_poly(
        r_root, c_root, r_start, chord_interp(r_start), chord_interp(r_start, 1)
    )

    # Find max val
    r_cmax = np.max(poly.deriv().roots)
    c_max_eval = poly(r_cmax)
    return c_max_eval - c_max


def _get_poly(r_root, c_root, r_start, c_start, dcdr_start):
    return poly_fit(
        [r_root, r_root, r_start, r_start],
        [c_root, 0.0, c_start, dcdr_start],
        [0, 1, 0, 1],
    )


def poly_fit(x, y, dev_order):
    """Polynomial fit for a given set of constraints.
    The order of the polynomial are determined from the length of x.

    Parameters
    ----------
    x : list, np.ndarray
        x value for the constraints
    y : list, np.ndarray
        value of the constraints
    dev_order : list, np.ndarray
        Derivatives order for the given constraint
        (0:f(x)=y, 1:df/dx(x)=y, 2:d2f/dx2(x)=y)

    Returns
    -------
    np.poly1d
        Polynomial that satisfy the given constraints
    """
    n = len(x)
    lhs = np.zeros([n] * 2)
    rhs = np.zeros(n)
    exps = np.arange(n)
    if dev_order is None:
        dev_order = np.zeros(n)
    for i, (_x, _y, _order) in enumerate(zip(x, y, dev_order)):
        if _order == 0:
            for j in range(n):
                lhs[i, j] = _x ** exps[j]
        elif _order == 1:
            for j in range(n):
                if exps[j] == 0:
                    continue
                lhs[i, j] = exps[j] * _x ** (exps[j] - 1)
        elif _order == 2:
            for j in range(n):
                if (exps[j] == 0) or (exps[j] == 1):
                    continue
                lhs[i, j] = exps[j] * (exps[j] - 1) * _x ** (exps[j] - 2)
        rhs[i] = _y

    coeffs = np.linalg.solve(lhs, rhs)
    poly = np.poly1d(list(coeffs[::-1]))

    # Testing Values
    for i, (_x, _y, _order) in enumerate(zip(x, y, dev_order)):
        np.testing.assert_almost_equal(_y, poly.deriv(_order)(_x), 10)
    return poly


def max_twist(twist, twist_max):
    """Limit a twist distribution at a given max twist

    Parameters
    ----------
    twist : np.ndarray
        twist distribution
    twist_max : float
        maximum twist angle

    Returns
    -------
    np.ndarray
        twist distribution constraint not to exceed the maximum twist angle
    """
    return np.minimum(twist, twist_max)


class interpolator(PchipInterpolator):
    """Pchip-interpolator creates a smooth curve from a set of data points
    This is just a simple wrapper around ``scipy.interpolate.PchipInterpolator``.
    For more info see: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html

    Parameters
    ----------
    x : list or np.ndarray
        Independent values to use for the interpolation
    y : list or np.ndarray
        Dependent value to use for the interpolation
    axis : int, optional
        Axis in the y array corresponding to the x-coordinate values.
    extrapolate : bool, optional
        Whether to extrapolate to out-of-bounds points based on first
        and last intervals, or to return NaNs.

    Returns
    -------
    PchipInterpolator instance
        The instance can be called with a new independent value to give an interpolated value
    """

    pass
