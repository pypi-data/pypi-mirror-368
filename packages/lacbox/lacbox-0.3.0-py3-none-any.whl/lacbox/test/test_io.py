# import os
from pathlib import Path

import numpy as np
import pytest

from lacbox.io import (
    load_pc, load_st, load_oper,
    save_pc, save_st, save_oper,
    load_ctrl_txt,
    ReadHAWC2
    )
from lacbox.test import test_data_path


TEST_DATA_DIR = Path(test_data_path)
DTU10_DATA_DIR = TEST_DATA_DIR / 'dtu_10_mw' / 'data'


def test_load_save_pc(tmpdir):
    # Load DTU 10MW pc file and test shape (1 set, should only return a list of prof data)
    pc_path = TEST_DATA_DIR  / 'uneven_pc.dat'
    pc_data = load_pc(pc_path)
    assert isinstance(pc_data, list)
    assert len(pc_data) == 6
    assert not isinstance(pc_data[0], list)
    assert pc_data[0]["tc"] == 24.1
    for prof, naoa in zip(pc_data, [99, 100, 101, 102, 103, 104]):
        for name in ["aoa_deg", "cl", "cd", "cm"]:
            assert prof[name].shape == (naoa,)
    
    # Write pc file with 1 set
    pc_path = tmpdir / "DTU_10MW_RWT_pc_1set_DEMO.dat"
    save_pc(pc_path, pc_data)
    
    # Write pc file with 2 sets
    pc_path = tmpdir / "DTU_10MW_RWT_pc_2sets_DEMO.dat"
    save_pc(pc_path, [pc_data, pc_data[2:5]])
    
    # Read pc file with 2 sets
    pc_data = load_pc(pc_path)
    assert isinstance(pc_data, list)
    assert len(pc_data) == 2
    assert isinstance(pc_data[0], list)
    assert len(pc_data[0]) == 6
    assert len(pc_data[1]) == 3
    assert pc_data[0][0]["tc"] == 24.1
    assert pc_data[1][0]["tc"] == 36.0
    # set 1
    for prof, naoa in zip(pc_data[0], [99, 100, 101, 102, 103, 104]):
        for name in ["aoa_deg", "cl", "cd", "cm"]:
            assert prof[name].shape == (naoa,)
    # set 2
    for prof, naoa in zip(pc_data[1], [101, 102, 103]):
        for name in ["aoa_deg", "cl", "cd", "cm"]:
            assert prof[name].shape == (naoa,)
    
    # Read 1 set from pc file with 2 sets
    pc_data = load_pc(pc_path, 2)
    assert isinstance(pc_data, list)
    assert len(pc_data) == 3
    assert pc_data[0]["tc"] == 36.0
    # set 2
    for prof, naoa in zip(pc_data, [101, 102, 103]):
        for name in ["aoa_deg", "cl", "cd", "cm"]:
            assert prof[name].shape == (naoa,)
    
    # should fail
    with pytest.raises(ValueError):
        save_pc(pc_path, object())
    with pytest.raises(ValueError):
        save_pc(pc_path, [object()])
    with pytest.raises(ValueError):
        save_pc(pc_path, dict())


def test_load_save_st(tmpdir):
    # Load DTU 10MW Blade st file (1 set and 2 subsets)
    st_path = DTU10_DATA_DIR / "DTU_10MW_RWT_Blade_st.dat"
    st_data = load_st(st_path)
    assert isinstance(st_data, list)
    assert len(st_data) == 1
    assert isinstance(st_data[0], list)
    assert len(st_data[0]) == 2
    for set in st_data:
        for subset in set:
            for name, val in subset.items():
                assert val.shape == (51,)
    # Write DTU 10MW blade st file
    st_path = tmpdir / "DTU_10MW_RWT_Blade_st_DEMO.dat"
    save_st(st_path, st_data)
    # Write 1 set (only a list of subsets)
    st_path = tmpdir / "DTU_10MW_RWT_Blade_st_2subsets_DEMO.dat"
    save_st(st_path, st_data[0])
    # Write 1 set (only a list of subsets)
    st_path = tmpdir / "DTU_10MW_RWT_Blade_st_1subset_DEMO.dat"
    save_st(st_path, st_data[0][0])
    # Write 2 set
    st_path = tmpdir / "DTU_10MW_RWT_Blade_st_2set_DEMO.dat"
    new_set = [st_data[0][0], st_data[0][0], st_data[0][1]]
    save_st(st_path, [st_data[0], new_set])
    # Load 2 set
    st_data = load_st(st_path)
    assert isinstance(st_data, list)
    assert len(st_data) == 2
    assert isinstance(st_data[0], list)
    assert len(st_data[0]) == 2
    assert isinstance(st_data[1], list)
    assert len(st_data[1]) == 3
    for set in st_data:
        for subset in set:
            for name, val in subset.items():
                assert val.shape == (51,)
    # Load 1 set
    st_data = load_st(st_path, 1)
    assert len(st_data) == 3
    assert isinstance(st_data[0], dict)
    for subset in st_data:
        for name, val in subset.items():
            assert val.shape == (51,)
    # Load the same subset for all sets
    st_data = load_st(st_path, dsubset=0)
    assert len(st_data) == 2
    assert isinstance(st_data[0], dict)
    assert isinstance(st_data[1], dict)
    for set in st_data:
        for name, val in set.items():
            assert val.shape == (51,)
    # Load a specific subset
    st_data = load_st(st_path, 1, 2)
    assert isinstance(st_data, dict)
    for name, val in st_data.items():
        assert val.shape == (51,)

    # should fail
    with pytest.raises(ValueError):
        save_st(st_path, object())
    with pytest.raises(ValueError):
        save_st(st_path, [object()])


def test_load_save_oper(tmpdir):
    # Load data with a single oper point (without power and thrust)
    oper_path =  DTU10_DATA_DIR / "operation_data.dat"
    oper_data = load_oper(oper_path)
    assert isinstance(oper_data, dict)
    assert len(oper_data) == 3
    for name, val in oper_data.items():
        assert val.shape == (1,)

    # Write same data out
    oper_path = tmpdir / "operation_data_DEMO.dat"
    save_oper(oper_path, oper_data)

    # Multipoint oper
    oper_data["ws_ms"] = [4, 5, 6, 7, 8]
    oper_data["pitch_deg"] = [0.0]*len(oper_data["ws_ms"])
    oper_data["rotor_speed_rpm"] = [10.0]*len(oper_data["ws_ms"])
    oper_path =  tmpdir / "operation_data_multipoint_DEMO.dat"
    save_oper(oper_path, oper_data)

    # Multipoint with power and thrust
    oper_data["power_kw"] = [1e6]*len(oper_data["ws_ms"])
    oper_data["thrust_kn"] = [1e5]*len(oper_data["ws_ms"])
    oper_path = tmpdir / "operation_data_multipoint_pt_DEMO.dat"
    save_oper(oper_path, oper_data)

    # Load oper with power and thrust
    save_oper(oper_path, oper_data)
    oper_data = load_oper(oper_path)
    assert isinstance(oper_data, dict)
    assert len(oper_data) == 5
    for name, val in oper_data.items():
        assert val.shape == (5,)


def test_load_gtsdf():
    """Try loading a gtsdf file"""
    # given
    path = TEST_DATA_DIR / 'dtu_10mw_turb.hdf5'
    # when
    h2res = ReadHAWC2(path)
    names, units, desc = h2res.chaninfo
    t = h2res.t
    # then
    assert names[0] == 'Time'
    assert names[9] == 'Omega'
    np.testing.assert_almost_equal(t[0], 100.01)
    

def test_load_ctrl_tune():
    """Check we load ctrl_tune correct"""
    # given
    path = TEST_DATA_DIR / 'dtu_10mw_hawc2s_ctrltune_ctrl_tuning.txt'
    # when
    ctrl_dict = load_ctrl_txt(path)
    # then
    assert len(ctrl_dict) == 12
    assert np.isclose(ctrl_dict['K_Nm/(rad/s)^2'], 0.101356E+08)
    assert np.isclose(ctrl_dict['Ko2_deg^2'], 7.27748)
    assert ctrl_dict['aero_gains'].shape[1] == 4
