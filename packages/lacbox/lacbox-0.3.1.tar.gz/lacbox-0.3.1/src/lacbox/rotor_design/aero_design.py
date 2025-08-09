import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brenth

from .utils import max_twist, min_tc_chord, root_chord


def get_design_functions(i_des_funs):
    """Gives the design functions for Cl [-], Cd [-], AoA [deg] as a function of Relative profile thickness (t/c) [%] (0-100).
    As well as the values used to construct the interpolation data.

    Parameters
    ----------
    i_des_funs : int
        Integer for selecting design functions (1-3)

    Returns
    -------
    tuple

        1. Lift coefficient function (`cl(tc)`)
        2. Drag coefficient function (`cd(tc)`)
        3. Angle-of-Attack function (`aoa(tc)`)
        4. Values of relative airfoil profile thickness (`tc`)
        5. Values of the lift coefficient (`cl`)
        6. Values of the drag coefficient (`cd`)
        7. Values of angle-of-attack (`aoa`)


    Raises
    ------
    ValueError
        If `i_des_funs` is out of range 1-3
    """
    tc = [0.0, 24.1, 30.1, 36.0, 48.0, 100, 105]
    if i_des_funs == 1:
        cl = [
            1.5138999999999958,
            1.5138999999999958,
            1.4326999999999999,
            1.3989,
            0.7425000000000018,
            0.0,
            0.0,
        ]
        cd = [
            0.014552013593356018,
            0.014552013593356018,
            0.017075689725789673,
            0.021377442022081927,
            0.03254612318627829,
            0.6,
            0.6,
        ]
        aoa = [
            10.127611178447252,
            10.127611178447252,
            9.435582501283362,
            6.07329414569828,
            3.0888580446417984,
            0.0,
            0.0,
        ]
    elif i_des_funs == 2:
        cl = [
            1.4139000000000002,
            1.4139000000000002,
            1.3327000000000164,
            1.298900000000027,
            0.6424999999999994,
            0.0,
            0.0,
        ]
        cd = [
            0.013462912738467942,
            0.013462912738467942,
            0.015682551073785765,
            0.020596371772063263,
            0.031826912205649135,
            0.6,
            0.6,
        ]
        aoa = [
            9.144287559414455,
            9.144287559414455,
            8.433574310138903,
            5.2970754586135556,
            2.508863954575325,
            0.0,
            0.0,
        ]
    elif i_des_funs == 3:
        cl = [
            1.3139000000000003,
            1.3139000000000003,
            1.2327000000000181,
            1.1989000000000005,
            0.5424999999999994,
            0.0,
            0.0,
        ]
        cd = [
            0.012579957352588572,
            0.012579957352588572,
            0.014718626752795042,
            0.019964317086192902,
            0.0316254735803436,
            0.6,
            0.6,
        ]
        aoa = [
            8.207286609806989,
            8.207286609806989,
            7.49309479479005,
            4.558616035847117,
            1.836019107496301,
            0.0,
            0.0,
        ]
    else:
        raise ValueError(
            f"i_des_funs={i_des_funs} is not a valid value. Should between 1-3."
        )

    return (
        PchipInterpolator(tc, cl),
        PchipInterpolator(tc, cd),
        PchipInterpolator(tc, aoa),
        np.array(tc[1:-2]),
        np.array(cl[1:-2]),
        np.array(cd[1:-2]),
        np.array(aoa[1:-2]),
    )


def get_design_functions_1MW(cl_scale=1.0):
    """Returns the design functions for Cl [-], Cd [-], AoA [deg] as a function of Relative profile thickness (t/c) [%] (0-100) for the 1MW example

    Parameters
    ----------
    cl_scale : float
        Scale factor multiplied for the Cl-values. Default is `cl_scale=1.0` yielding the baseline cl_design.

    Returns
    -------
    tuple

        1. Lift coefficient function (`cl(tc)`)
        2. Drag coefficient function (`cd(tc)`)
        3. Angle-of-Attack function (`aoa(tc)`)
        4. Values of relative airfoil profile thickness (`tc`)
        5. Values of the lift coefficient (`cl`)
        6. Values of the drag coefficient (`cd`)
        7. Values of angle-of-attack (`aoa`)

    """
    tc = [0, 15, 18, 24, 30, 36, 100, 105]
    cl = np.array([0.9, 0.9, 0.8, 0.8, 0.7, 0.6, 0.0, 0.0]) * cl_scale
    cd = [0.00850, 0.00850, 0.00604, 0.0107, 0.0139, 0.0155, 0.5, 0.5]
    aoa = [5.0, 5.0, 4.3, 4.3, 4.0, 0.5, 0.0, 0.0]
    return (
        PchipInterpolator(tc, cl),
        PchipInterpolator(tc, cd),
        PchipInterpolator(tc, aoa),
        np.array(tc[1:-2]),
        np.array(cl[1:-2]),
        np.array(cd[1:-2]),
        np.array(aoa[1:-2]),
    )


def ap_fun(a, tsr, rt):
    """Computes tangential induction

    Parameters
    ----------
    a : float
        Design axial induction [-]
    tsr : float
        tip-speed-ratio (`rotor_speed*R/V0`) [-]
    rt : float or np.dnarray
        normalized rotor span (r/R) [-]

    Returns
    -------
    float or np.ndarray
        tangential induction factor at a given `rt` [-]
    """
    return (np.sqrt(1 + 4 * a * (1 - a) / (tsr * rt) ** 2) - 1) / 2


def Vt_rel_fun(a, tsr, rt):
    """Computes normalized relative wind speed (`V_rel=V*Vt_rel`)

    Parameters
    ----------
    a : float
        Design axial induction [-]
    tsr : float
        tip-speed-ratio (`rotor_speed*R/V0`) [-]
    rt : float or np.dnarray
        normalized rotor span (r/R) [-]

    Returns
    -------
    float or np.ndarray
        normalized relative wind speed at a given `rt` [-]
    """
    ap = ap_fun(a, tsr, rt)
    return np.sqrt((1 - a) ** 2 + tsr**2 * rt**2 * (1 + ap) ** 2)


def cos_phi_fun(a, tsr, rt):
    """Computes cosine of the flow angle (`cos_phi=tsr*rt*(1+ap)/Vt_rel`)

    Parameters
    ----------
    a : float
        Design axial induction [-]
    tsr : float
        tip-speed-ratio (`rotor_speed*R/V0`) [-]
    rt : float or np.dnarray
        normalized rotor span (r/R) [-]

    Returns
    -------
    float or np.ndarray
        cosine of the flow angle at a given `rt` [-]
    """
    ap = ap_fun(a, tsr, rt)
    Vt_rel = Vt_rel_fun(a, tsr, rt)
    return tsr * rt * (1 + ap) / Vt_rel


def tan_phi_fun(a, tsr, rt):
    """Computes tangent of the flow angle (`tan_phi=(1-a)/(tsr*rt*(1+ap))`)

    Parameters
    ----------
    a : float
        Design axial induction [-]
    tsr : float
        tip-speed-ratio (`rotor_speed*R/V0`) [-]
    rt : float or np.dnarray
        normalized rotor span (r/R) [-]

    Returns
    -------
    float or np.ndarray
        tangent of the flow angle at a given `rt` [-]
    """
    ap = ap_fun(a, tsr, rt)
    return (1 - a) / (tsr * rt * (1 + ap))


def sin_phi_fun(a, tsr, rt):
    """Computes sinus of the flow angle (`sin_phi=(1-a)/Vt_rel`)

    Parameters
    ----------
    a : float
        Design axial induction [-]
    tsr : float
        tip-speed-ratio (`rotor_speed*R/V0`) [-]
    rt : float or np.dnarray
        normalized rotor span (r/R) [-]

    Returns
    -------
    float or np.ndarray
        sinus of the flow angle at a given `rt` [-]
    """
    Vt_rel = Vt_rel_fun(a, tsr, rt)
    return (1 - a) / Vt_rel


def F_fun(a, tsr, rt, B):
    """Computes Glauerts tip-loss factor (`F`)

    Parameters
    ----------
    a : float
        Design axial induction [-]
    tsr : float
        tip-speed-ratio (`rotor_speed*R/V0`) [-]
    rt : float or np.dnarray
        normalized rotor span (r/R) [-]
    B : int
        Number of rotor blades [#]

    Returns
    -------
    float or np.ndarray
        Glauerts tip-loss factor at a given `rt` [-]
    """
    sin_phi = sin_phi_fun(a, tsr, rt)
    return 2 / np.pi * np.arccos(np.exp(-(B * (1 - rt) / (2 * rt * sin_phi))))


@np.vectorize
def CLT_momentum(a, F):
    """Relationship between the axial flow momentum and normal loading

    Parameters
    ----------
    a : float or ndarray of floats
        Values for axial-induction [-]
    F : float or ndarray of floats
        Value for the tiploss factor [-]

    Returns
    -------
    float or ndarray of floats
        Local-thrust values
    """
    if a >= 0.4:
        return (8 / 9 + (4 - 40 / 9) * a + (50 / 9 - 4) * a**2) * F
    else:
        return 4 * a * (1 - a) * F


def a_momentum_HAWC2(CLT, F):
    """HAWC2 polynomial relationship between axial-induction (`a`) and local-thrust (`CLT`)

    Parameters
    ----------
    CLT : float or ndarray of floats
        Value for local thrust [-]
    F : float or ndarray of floats
        Value for the tiploss factor [-]

    Returns
    -------
    float or ndarray
        Axial-induction (`a`)[-]
    """
    A = 0.0883
    B = 0.0586
    C = 0.2460
    return A * (CLT / F) ** 3 + B * (CLT / F) ** 2 + C * (CLT / F)


@np.vectorize
def solve_CLT_momentum_HAWC2(a, F):
    """Solves the HAWC2 polynomial for local-thrust (`CLT`) for a given axial-induction (`a`)

    Parameters
    ----------
    a : float or ndarray of floats
        Values for axial-induction [-]
    F : float or ndarray of floats
        Value for the tiploss factor [-]

    Returns
    -------
    float or ndarray
        Local-thrust (`CLT`) [-]
    """

    def obj(CLT, a, F):
        return a_momentum_HAWC2(CLT, F) - a

    a_glauert = CLT_momentum(a, F)
    return brenth(obj, a_glauert - 0.2, a_glauert + 0.2, (a, F))


def f_flow_fun(a, tsr, rt, B, R, use_HAWC2_poly=True):
    """Computes the `f_flow` function (`f_flow = 8*pi*r*a*(1-a)*F/(B*Vt_rel**2*cos_phi)`)

    Parameters
    ----------
    a : float
        Design axial induction [-]
    tsr : float
        tip-speed-ratio (`rotor_speed*R/V0`) [-]
    rt : float or np.dnarray
        normalized rotor span (r/R) [-]
    B : int
        Number of rotor blades [#]
    R : float
        Rotor radius [m]
    use_HAWC2_poly :  bool
        Flag for using the the HAWC2 a-CT relation (default=False)

    Returns
    -------
    float or np.ndarray
        f_flow at a given `rt` [-]
    """
    r = rt * R
    Vt_rel = Vt_rel_fun(a, tsr, rt)
    cos_phi = cos_phi_fun(a, tsr, rt)
    F = F_fun(a, tsr, rt, B)
    if use_HAWC2_poly:
        CLT = solve_CLT_momentum_HAWC2(a, F)
    else:
        CLT = CLT_momentum(a, F)
    return 2 * np.pi * r * CLT / (B * Vt_rel**2 * cos_phi)


def residual(tc, f_flow, t, cl_des):
    """Computes the residual function. Function to be solved: `cl_des(tc) = f_flow/t*tc` where `tc` is the unknown.

    Parameters
    ----------
    tc : float
        relative thickness guess (`tc=0-100`) [%]
    f_flow : float
        value of the f_flow function [m]
    t : float
        absolute thickness for the blade [m]
    cl_des : callable
        function that returns Cl for a given t/c [%] (t/c=0-100) [-]

    Returns
    -------
    float
        value of the residual (root solution is found when residual is zero)
    """
    return cl_des(tc) - f_flow / t * tc / 100


def solve_tc(cl_des, r, t, tsr, R, a, B, tc_bounds=(0, 100), use_HAWC2_poly=True):
    """Solves for the relative thickness (t/c) for a given Cl-design function and flow conditions

    Parameters
    ----------
    cl_des : callable
        function that returns Cl for a given t/c [%] (t/c=0-100) [-]
    r : np.ndarray
        rotor span (including hub radius) [m]
    t : np.ndarray
        Absolute blade thickness [m]
    tsr : float
        tip-speed-ratio (rotor_speed*R/V0) [-]
    R : float
        Rotor radius [m]
    a : float
        Design axial induction [-]
    B : int
        Number of rotor blades [#]
    tc_bounds : tuple, optional
        range for the root solver to look for a solution (end points should enclose the solution), by default (0, 100)
    use_HAWC2_poly :  bool
        Flag for using the the HAWC2 a-CT relation (default=False)

    Returns
    -------
    np.ndarray
        relative thickness (t/c) along the blade span [%] (chord can be computed as chord=t/(tc/100))

    Raises
    ------
    Exception
        if a solution is not found at a given radius it will fail a indicated at which radius it failed
    """
    if any(r >= R):
        raise ValueError(
            f"Some values for r is larger or equal to R, all values should be strictly less than R (given r/R={r/R})"
        )

    tcs = np.empty_like(r)  # initialize t/c output array
    for i, (_r, _t) in enumerate(zip(r, t)):
        rt = _r / R
        f_flow = f_flow_fun(a, tsr, rt, B, R, use_HAWC2_poly)
        args = (f_flow, _t, cl_des)  # Arguments passed to the residual function
        try:
            tcs[i] = brenth(residual, *tc_bounds, args)
        except:
            raise Exception(
                f"solve_tc failed to find a solution. It failed at index={i} coresponding to a span location of r={_r:2.2f}"
            )
    return tcs


def bem_residual(a, r, tsr, R, chord, cl, B, use_HAWC2_poly=True):
    """Residual for BEM equations

    Parameters
    ----------
    a : float
        Value for axial-induction [-]
    r : float
        Span [m]
    tsr : float
        Tip-speed-ratio [-]
    R : float
        Rotor radius [m]
    chord : float
        Rotor chord [m]
    cl : float
        Lift coefficient [-]
    B : float
        Number of blades [#]
    use_HAWC2_poly : bool, optional
        Flag for using the the HAWC2 a-CT relation, by default False

    Returns
    -------
    float
        Residual to be zero when solving for axial induction
    """
    rt = r / R
    f_flow = f_flow_fun(a, tsr, rt, B, R, use_HAWC2_poly)
    return chord * cl - f_flow


def solve_bem(r, tsr, R, chord, cl, B, a_bounds=(-1e-3, 0.9), use_HAWC2_poly=True):
    """Solves the BEM equation for axial-induction (`a`)

    Parameters
    ----------
    r : ndarray of floats
        Span [m]
    tsr : float
        Tip-speed-ratio [-]
    R : float
        Rotor radius [m]
    chord : ndarray of floats
        Rotor chord [m]
    cl : float or ndarray of floats
        Lift coefficient [-]
    B : float
        Number of blades [#]
    a_bounds : tuple, optional
        Bounds for brenth root-solver solver, by default (0, 0.9)
    use_HAWC2_poly : bool, optional
        Flag for using the the HAWC2 a-CT relation, by default False

    Returns
    -------
    ndarray
        Axial-induction that satisfy the BEM equation for given input

    Raises
    ------
    Exception
        if a solution is not found at a given radius it will fail a indicated at which radius it failed
    """
    if not hasattr(cl, "__len__"):
        cl = np.full_like(r, cl)
    a = np.empty_like(r)  # initialize t/c output array
    for i, (_r, _c, _cl) in enumerate(zip(r, chord, cl)):
        args = (
            _r,
            tsr,
            R,
            _c,
            _cl,
            B,
            use_HAWC2_poly,
        )  # Arguments passed to the residual function
        try:
            a[i] = brenth(bem_residual, *a_bounds, args)
        except:
            raise Exception(
                f"solve_bem failed to find a solution. It failed at index={i} coresponding to a span location of r={_r:2.2f}"
            )
    return a


def chord_fun(r, tsr, R, a, B, cl, use_HAWC2_poly=True):
    """Computes the chord by knowing the Cl along the span

    Parameters
    ----------
    r : np.ndarray
        rotor span (including hub radius) [m]
    tsr : float
        tip-speed-ratio (rotor_speed*R/V0) [-]
    R : float
        Rotor radius [m]
    a : float
        Design axial induction [-]
    B : int
        Number of rotor blades [#]
    cl : np.ndarray
        cl design along the span [-]
    use_HAWC2_poly :  bool
        Flag for using the the HAWC2 a-CT relation (default=False)

    Returns
    -------
    np.ndarray
        chord along the rotor span [m]
    """
    rt = r / R
    return f_flow_fun(a, tsr, rt, B, R, use_HAWC2_poly) / cl


def twist_deg_fun(r, tsr, R, a, aoa):
    """Computes the twist for a given design Angle-of-Attack

    Parameters
    ----------
    r : np.ndarray
        rotor span (including hub radius) [m]
    tsr : float
        tip-speed-ratio (rotor_speed*R/V0) [-]
    R : float
        Rotor radius [m]
    a : float
        Design axial induction [-]
    aoa : np.ndarray
        design angle-of-attack along the span [deg]

    Returns
    -------
    np.ndarray
        twist along the rotor span [deg]
    """
    rt = r / R
    return np.rad2deg(np.arctan(tan_phi_fun(a, tsr, rt))) - aoa


def CLT_fun(r, tsr, R, a, B, cl, cd, chord):
    """Computes the local-thrust-coefficient (normal force per blade `f_n = rho*pi*r*V**2*CLT/B`)

    Parameters
    ----------
    r : np.ndarray
        rotor span (including hub radius) [m]
    tsr : float
        tip-speed-ratio (rotor_speed*R/V0) [-]
    R : float
        Rotor radius [m]
    a : float
        Design axial induction [-]
    B : int
        Number of rotor blades [#]
    cl : np.ndarray
        cl design along the span [-]
    cd : np.ndarray
        cd design along the span [-]
    chord : np.ndarray
        chord along the span [m]

    Returns
    -------
    np.ndarray
        local-thrust-coefficient along the rotor span [-]
    """
    rt = r / R
    solidity = B * chord / (2 * np.pi * rt * R)
    Vt_rel = Vt_rel_fun(a, tsr, rt)
    cos_phi = cos_phi_fun(a, tsr, rt)
    sin_phi = sin_phi_fun(a, tsr, rt)
    return solidity * Vt_rel**2 * (cl * cos_phi + cd * sin_phi)


def CLP_fun(r, tsr, R, a, B, cl, cd, chord):
    """Computes the local-power-coefficient (tangential force per blade `f_t = rho*pi*R*V**2*CLP/(tsr*B)`)

    Parameters
    ----------
    r : np.ndarray
        rotor span (including hub radius) [m]
    tsr : float
        tip-speed-ratio (rotor_speed*R/V0) [-]
    R : float
        Rotor radius [m]
    a : float
        Design axial induction [-]
    B : int
        Number of rotor blades [#]
    cl : np.ndarray
        cl design along the span [-]
    cd : np.ndarray
        cd design along the span [-]
    chord : np.ndarray
        chord along the span [m]

    Returns
    -------
    np.ndarray
        local-power-coefficient along the rotor span [-]
    """
    rt = r / R
    solidity = B * chord / (2 * np.pi * rt * R)
    Vt_rel = Vt_rel_fun(a, tsr, rt)
    cos_phi = cos_phi_fun(a, tsr, rt)
    sin_phi = sin_phi_fun(a, tsr, rt)
    return tsr * rt * solidity * Vt_rel**2 * (cl * sin_phi - cd * cos_phi)


def CT_fun(r, R, CLT):
    """Computes the global-thrust coefficient (CT) using trapezoidal-integration along the rotor span (thrust force `T = 0.5*rho*pi*R**2*V**2*CT`   )

    Parameters
    ----------
    r : np.ndarray
        rotor span (including hub radius) [m]
    R : float
        Rotor radius [m]
    CLT : np.ndarray
        local-thrust-coefficient along the rotor span [-]

    Returns
    -------
    float
        Thrust-coefficient
    """
    rt = r / R
    return np.trapezoid(2 * CLT * rt, rt)


def CP_fun(r, R, CLP):
    """Computes the global-power-coefficient (CT) using trapezoidal-integration along the rotor span (aerodynamic power `P = 0.5*rho*pi*R**2*V**3*CP`)

    Parameters
    ----------
    r : np.ndarray
        rotor span (including hub radius) [m]
    R : float
        Rotor radius [m]
    CLP : np.ndarray
        local-power-coefficient along the rotor span [-]

    Returns
    -------
    float
        Power-coefficient
    """
    rt = r / R
    return np.trapezoid(2 * CLP * rt, rt)


def single_point_design(
    r, t, tsr, R, cl_des, cd_des, aoa_des, chord_root, chord_max, B, a=1 / 3
):
    """Function for creating (chord, twist, relative-thickness) and evaluating the design (CP, CT, ..)

    Parameters
    ----------
    r : np.ndarray
        rotor span (including hub radius) [m]
    t : np.ndarray
        Absolute blade thickness [m]
    tsr : float
        tip-speed-ratio (`rotor_speed*R/V0`) [-]
    R : float
        Rotor radius [m]
    cl_des : callable
        function that returns Cl for a given t/c [%] (t/c=0-100) [-]
    cd_des : callable
        function that returns Cd for a given t/c [%] (t/c=0-100) [-]
    cl_des : callable
        function that returns AoA for a given t/c [%] (t/c=0-100) [-]
    chord_root : float
        Chord size at the root of the blade (assuming blade root to be at r[0]) [m]
    chord_max : float
        Maximum chord size [m]
    B : int
        Number of rotor blades [#]
    a : float
        Design axial induction. Default to `a=1/3` [-]


    Returns
    -------
    dict

        chord : np.ndarray
            Blade chord [m]

        tc : np.ndarray
            Blade relative blade thickness [%]

        twist : np.ndarray
            Blade twist (opposite sign to HAWC2) [deg]

        cl : np.ndarray
            Lift coefficient [-]

        cd : np.ndarray
            Drag coefficient [-]

        aoa : np.ndarray
            Angle of attack [deg]

        a : np.ndarray
            Axial induction factor [-]

        CLT : np.ndarray
            Local Thrust Coefficient [-]

        CLP : np.ndarray
            Local Power Coefficient [-]

        CT : float
            Global Thrust Coefficient [-]

        CP : float
            Global Power Coefficient [-]

    """
    # Solving for t/c
    tc_ideal = solve_tc(cl_des, r, t, tsr, R, a, B)

    # Compute chord and twist

    # Getting ideal aero cl (before changing chord)
    cl_ideal = cl_des(tc_ideal)  # [-]

    # Chord [m]
    chord_ideal = chord_fun(r, tsr, R, a, B, cl_ideal)  # calculating ideal chord
    chord = root_chord(
        r, chord_ideal, chord_root, chord_max
    )  # transition from ideal to root chord
    chord = min_tc_chord(chord, t)  # maintain minimum t/c at the tip

    # Updating t/c and polar design values
    tc = t / chord * 100
    cl = cl_des(tc)  # [-]
    cd = cd_des(tc)  # [-]
    aoa_ideal = aoa_des(tc)  # [deg]

    # Twist [deg]
    twist_ideal = twist_deg_fun(r, tsr, R, a, aoa_ideal)  # [deg]
    twist = max_twist(twist_ideal, 20)  # Limiting the twist angle at 20 degrees

    # Updating a
    a = solve_bem(r, tsr, R, chord, cl, B)

    # Updating aoa
    aoa = (
        twist_deg_fun(r, tsr, R, a, 0) - twist
    )  # Updating the design aoa for the constraint twist

    # Compute local- and global-thrust-coefficient as well as local- and global-power-coefficient
    CLT = CLT_fun(r, tsr, R, a, B, cl, cd, chord)
    CLP = CLP_fun(r, tsr, R, a, B, cl, cd, chord)
    CT = CT_fun(r, R, CLT)
    CP = CP_fun(r, R, CLP)
    return dict(
        chord=chord,
        tc=tc,
        twist=twist,
        cl=cl,
        cd=cd,
        aoa=aoa,
        a=a,
        CLT=CLT,
        CLP=CLP,
        CT=CT,
        CP=CP,
    )
