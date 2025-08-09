import numpy as np
import pytest

from lacbox.rotor_design import aero_design
from lacbox.rotor_design.utils import min_tc_chord, root_chord


def test_ap_a_relationship():
    n = 100
    a = np.linspace(0, 0.4, n)
    tsr = 10
    rt = np.linspace(0.05, 1, n)

    ap = aero_design.ap_fun(a, tsr, rt)
    np.testing.assert_almost_equal(a * (1 - a), tsr**2 * rt**2 * ap * (1 + ap))


def test_flow_angle():
    n = 100
    a = np.linspace(0, 0.4, n)
    tsr = 10
    rt = np.linspace(0.05, 1, n)

    tan_phi = aero_design.tan_phi_fun(a, tsr, rt)
    cos_phi = aero_design.cos_phi_fun(a, tsr, rt)
    sin_phi = aero_design.sin_phi_fun(a, tsr, rt)
    np.testing.assert_almost_equal(tan_phi, sin_phi / cos_phi)


def test_tiploss_factor():
    # Limit values
    a = 1 / 3
    tsr = 10
    np.testing.assert_almost_equal(aero_design.F_fun(a, tsr, 1e-9, 3), 1)
    np.testing.assert_almost_equal(aero_design.F_fun(a, tsr, 1, 3), 0)

    # Sensitivity to tsr
    n = 100
    rt = np.linspace(0.05, 1, n)
    assert all(aero_design.F_fun(a, tsr, rt, 3) >= aero_design.F_fun(a, tsr - 1, rt, 3))

    # Sensitivity to B
    assert all(aero_design.F_fun(a, tsr, rt, 3) >= aero_design.F_fun(a, tsr, rt, 2))


def test_CLT_momentum():
    n = 100
    a = np.linspace(0, 0.7, n)
    F = np.ones(n)

    CLT = aero_design.CLT_momentum(a, F)

    loc = a < 0.4
    np.testing.assert_almost_equal(CLT[loc], 4 * a[loc] * (1 - a[loc]))

    loc = a > 0.4
    assert all(CLT[loc] > 4 * a[loc] * (1 - a[loc]))

    assert aero_design.CLT_momentum(0.4, 1) == 4 * 0.4 * (1 - 0.4)


def test_HAWC2_poly():
    n = 100
    a = np.linspace(0, 0.7, n)
    tsr = 10
    rt = np.linspace(0.05, 1 - 1e-9, n)
    B = 3

    F = aero_design.F_fun(a, tsr, rt, B)
    CLT = aero_design.solve_CLT_momentum_HAWC2(a, F)
    np.testing.assert_almost_equal(a, aero_design.a_momentum_HAWC2(CLT, F))


def test_f_flow():
    n = 100
    a = np.linspace(0, 0.7, n)
    tsr = 10
    rt = np.linspace(0.05, 1 - 1e-9, n)
    B = 3
    R = 1

    F = aero_design.F_fun(a, tsr, rt, B)
    Vt_rel = aero_design.Vt_rel_fun(a, tsr, rt)
    cos_phi = aero_design.cos_phi_fun(a, tsr, rt)
    # Glauert+Buhl
    CLT = aero_design.CLT_momentum(a, F)
    np.testing.assert_array_almost_equal(
        aero_design.f_flow_fun(a, tsr, rt, B, R, False),
        2 * np.pi * rt * CLT / (B * Vt_rel**2 * cos_phi),
    )

    # HAWC2
    CLT = aero_design.solve_CLT_momentum_HAWC2(a, F)
    np.testing.assert_array_almost_equal(
        aero_design.f_flow_fun(a, tsr, rt, B, R, True),
        2 * np.pi * rt * CLT / (B * Vt_rel**2 * cos_phi),
    )


def test_solve_tc():
    R = 35  # length of blade [m]
    tsr = 9.0  # TSR [-]
    B = 3  # number of blades
    a = 1 / 3  # axial induction [-]
    r_hub = 1.0
    r = np.linspace(r_hub, R - 0.1, 40)  # Rotor span [m]
    chord_root = 2.7  # Chord at the root [m]

    # Aero dynamic polar design functions (t/c vs. cl, cl/cd, aoa and r vs. thickness)
    def thickness(r):
        """Absolute thickness [m] as a function of blade span [m] for 35-m blade"""
        p_edge = [
            9.35996e-8,
            -1.2911e-5,
            7.15038e-4,
            -2.03735e-2,
            3.17726e-1,
            -2.65357,
            10.2616,
        ]  # polynomial coefficients
        t_poly = np.polyval(p_edge, r)  # evaluate polynomial
        t = np.minimum(t_poly, chord_root)  # clip at max thickness
        return t

    # Design value (extended to have a valid range from 0-100 including zero tangent at the ends)
    cl_des, cd_des, aoa_des = aero_design.get_design_functions_1MW()[:3]

    # Solving for the relative thickness (t/c)
    # Computing absolute thickness
    t = thickness(r)

    # Solving for t/c
    tc_ideal = aero_design.solve_tc(cl_des, r, t, tsr, R, a, B)

    # Test that it raises an error if brenth did not solve
    with pytest.raises(Exception):
        tc_ideal = aero_design.solve_tc(cl_des, r, t, tsr, R, a, B, tc_bounds=(0, 1))

    # Test that it raises an error if r > R
    with pytest.raises(ValueError):
        r[-1] = R
        tc_ideal = aero_design.solve_tc(cl_des, r, t, tsr, R, a, B)


def test_solve_bem():
    # Inputs
    R = 35  # length of blade [m]
    tsr = 9.0  # TSR [-]
    B = 3  # number of blades
    a = 1 / 3  # axial induction [-]
    r_hub = 1.0
    r = np.linspace(r_hub, R - 0.1, 40)  # Rotor span [m]
    chord_max = 3.0  # Maximum chord size [m]
    chord_root = 2.7  # Chord at the root [m]

    # Aero dynamic polar design functions (t/c vs. cl, cl/cd, aoa and r vs. thickness)
    def thickness(r):
        """Absolute thickness [m] as a function of blade span [m] for 35-m blade"""
        p_edge = [
            9.35996e-8,
            -1.2911e-5,
            7.15038e-4,
            -2.03735e-2,
            3.17726e-1,
            -2.65357,
            10.2616,
        ]  # polynomial coefficients
        t_poly = np.polyval(p_edge, r)  # evaluate polynomial
        t = np.minimum(t_poly, chord_root)  # clip at max thickness
        return t

    # Design value (extended to have a valid range from 0-100 including zero tangent at the ends)
    cl_des, cd_des, aoa_des = aero_design.get_design_functions_1MW()[:3]

    # Solving for the relative thickness (t/c)
    # Computing absolute thickness
    t = thickness(r)

    # Solving for t/c
    tc_ideal = aero_design.solve_tc(cl_des, r, t, tsr, R, a, B)

    # Compute chord and twist

    # Getting ideal aero cl (before changing chord)
    cl_ideal = cl_des(tc_ideal)  # [-]

    # Chord [m]
    chord_ideal = aero_design.chord_fun(
        r, tsr, R, a, B, cl_ideal
    )  # calulating ideal chord
    chord = root_chord(
        r, chord_ideal, chord_root, chord_max
    )  # transition from ideal to root chord
    chord = min_tc_chord(chord, t)  # maintain minimum t/c at the tip

    # Updating t/c and polar design values
    tc = t / chord * 100
    cl = cl_des(tc)  # [-]

    # Updating a with Glauert+Buhl
    a = aero_design.solve_bem(r, tsr, R, chord, cl, B)
    np.testing.assert_almost_equal(
        aero_design.bem_residual(a, r, tsr, R, chord, cl, B), 0
    )

    # Updating a with HAWC2
    a = aero_design.solve_bem(r, tsr, R, chord, cl, B, use_HAWC2_poly=True)
    np.testing.assert_almost_equal(
        aero_design.bem_residual(a, r, tsr, R, chord, cl, B, use_HAWC2_poly=True),
        0,
    )


def test_CLT_CLP():
    n = 100
    a = np.full(n, 1 / 3)
    tsr = 1e100
    rt = np.linspace(1e-9, 1 - 1e-9, n)
    B = 3
    R = 1
    cl = 1
    cd = 0

    chord = aero_design.chord_fun(rt, tsr, R, a, B, cl, False)

    # Ensure Betz limit
    CLT = aero_design.CLT_fun(rt, tsr, R, a, B, cl, cd, chord)
    np.testing.assert_almost_equal(CLT, 8 / 9)
    CT = aero_design.CT_fun(rt, R, CLT)
    np.testing.assert_almost_equal(CT, 8 / 9)

    CLP = aero_design.CLP_fun(rt, tsr, R, a, B, cl, cd, chord)
    np.testing.assert_almost_equal(CLP, 16 / 27)
    CP = aero_design.CT_fun(rt, R, CLP)
    np.testing.assert_almost_equal(CP, 16 / 27)
