"""Loading and saving files."""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from lacbox import gtsdf

_OPER_NAMES = ["ws_ms", "pitch_deg", "rotor_speed_rpm", "power_kw", "thrust_kn"]
_ST_NAMES = [
    "s",
    "m",
    "x_cg",
    "y_cg",
    "ri_x",
    "ri_y",
    "x_sh",
    "y_sh",
    "E",
    "G",
    "I_x",
    "I_y",
    "I_p",
    "k_x",
    "k_y",
    "A",
    "pitch",
    "x_e",
    "y_e",
]
_AERO_GAIN_NAMES = [
    "theta_deg",
    "dq/dtheta_kNm/deg",
    "fit_kNm/deg",
    "dq/domega_kNm/(rad/s)",
    "fit_kNm/(rad/s)",
]


def load_ae(path, dset=1, unpack=False):
    """Load data in an AE file to a 2D numpy array or list of 1D arrays.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the AE file.
    dset : int, optional
        Dataset to load. NOTE that this function will only work with dset = 1.
    unpack : boolean, optional
        Whether to unpack the 2D array into a list of 1D arrays. The default is False.

    Returns
    -------
    ae : np.ndarray
        Either a 2D array with 4 columns or a list of 4 1D arrays, one for each column
        in the AE file.
    """
    if dset != 1:
        raise ValueError("Function only supports loading first dataset!")
    ae = np.loadtxt(path, skiprows=2, comments=";", unpack=unpack)
    return ae


def save_ae(path, ae_data):
    """Save the AE data in a 2D numpy array to HAWC2 file.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the AE file to save.
    ae_data : np.ndarray
        2D numpy array of AE data to be saved. Array should have 4 columns.
    """
    n_rows = ae_data.shape[0]  # no. of rows to save
    with open(path, "w") as ae_file:
        ae_file.write(f"1\n1  {n_rows}\n")  # header of AE file
        np.savetxt(
            ae_file, ae_data, fmt="%11.4e", delimiter="\t", newline="\t;\n", header=""
        )


def load_amp(path, exclude_modes=[1]):
    """Load modal amplitudes from .amp file.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the .amp file to load.
    exclude_modes : list (optional)
        List of HAWCStab2 modal indices (starting from 1) that should be excluded when
        loading. Useful to remove rigid-body or higher-frequency modes. Default value
        is `[1]`, which removes the first mode.

    Returns
    -------
    df : pd.Dataframe
        A pandas dataframe with `(n_wsp+1)` rows, corresponding to each wind speed plus
        one row to indicate the mode number. Each column corresponds to the amplitude of
        a given modal component for the given mode number.
    """
    df = pd.read_csv(path, delim_whitespace=True, comment="#", header=None)
    CHAR_PER_COL = 14
    with open(path, "r", encoding="utf-8") as f:
        for il, line in enumerate(f.readlines()):
            if il == 2:
                mode_numbers = [int(s) for s in line.split(":")[1].split()]
            elif il == 4:
                nchar = len(line)
                ncols = nchar // CHAR_PER_COL
                columns = [
                    line[i * CHAR_PER_COL : (i + 1) * CHAR_PER_COL]
                    .rstrip()
                    .lstrip("# ")
                    for i in range(ncols)
                ]
            elif il > 4:
                break
    df.loc["mode_number", :] = [np.nan] + mode_numbers
    df.columns = columns
    for imode in exclude_modes:
        df = df.loc[:, ~np.isclose(df.loc["mode_number"], imode)]
    return df


def load_cmb(path, cmb_type, exclude_rigid=True):
    """Load wsp, damped natural freqs, and damping from cmb file.

    Optionally remove a mode shape if the initial frequency is
    close to zero.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the htc with the twist to load.
    cmb_type : string
        Whether it is a structural (`cmb_type='structural'`) or aeroelastic
        (`cmb_type='aeroelastic'`) .cmb file.
    exclude_rigid : boolean (optional)
        If True, only load modes whose frequency at the lower wind speed is
        larger than zero.

    Returns
    -------
    wsp : np.ndarray
        The (n_wsp,) wind speeds calculated in the cmb file.
    dfreqs : np.ndarray
        A 2D array of shape (n_wsp, n_modes,) with the damped natural
        frequencies.
    zetas : np.ndarray
        A 2D array of shape (n_wsp, n_modes,) with the modal damping
        in percent critical.
    """
    arr = np.loadtxt(path)
    if cmb_type == "structural":
        nmodes = (arr.shape[1] - 1) // 2
    elif cmb_type == "aeroelastic":
        nmodes = (arr.shape[1] - 1) // 3
    else:
        raise ValueError(
            'Parameter "cmb_type" mus be either "structural" or "aeroelastic"!'
        )
    wsp = arr[:, 0]
    dfreqs = arr[:, 1 : nmodes + 1]
    zetas = arr[:, nmodes + 1 : 2 * nmodes + 1]
    if exclude_rigid:
        mask = ~np.isclose(dfreqs[0, :], 0)
        dfreqs = dfreqs[:, mask]
        zetas = zetas[:, mask]
    return wsp, dfreqs, zetas


def load_c2def(path, bodyname="blade1"):
    """Load the c2_def data from htc file.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the htc with the twist to load.
    bodyname : str, optional
        Name of the body for which you want to load the c2_def information. Default is
        'blade1'.

    Returns
    -------
    c2_def : np.ndarray
        A 2D numpy array with 4 columns, corresponding to the numerical data columns in
        the c2_def block (skipping the section number).
    """
    in_body = False
    with open(path, "r") as htc_file:
        for line in htc_file.readlines():
            linesplit = line.split(";")[0].split()
            if ("name" in linesplit) and (bodyname in linesplit):
                in_body = True
            if in_body:
                if "nsec" in linesplit:
                    nsec = int(linesplit[1])
                    c2_def = np.empty((nsec, 4))
                elif "sec" in linesplit:
                    idx = int(linesplit[1]) - 1
                    vals = [float(x) for x in linesplit[2:6]]
                    c2_def[idx, :] = vals
                elif ("end" in linesplit) and ("main_body" in linesplit):
                    in_body = False

    return c2_def


def save_c2def(path, c2_def, parspace="  "):
    """Save a c2_def array to a text file that can be copied into a htc file.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the text file that we want to create. NOT YOUR HTC FILE!
    c2_def : np.ndarray
        2D numpy array with 4 columns corresponding to x, y, z, and twist.
    parspace : str, optional
        The indentation delimiter. The default is 2 spaces.
    """
    nsec = c2_def.shape[0]
    with open(path, "w") as file:
        file.write(parspace + "begin c2_def;\n")
        file.write(2 * parspace + f"nsec {nsec};\n")
        for i, vals in enumerate(c2_def):
            file.write(
                2 * parspace
                + f"sec {i+1:2.0f}{vals[0]:15.5e}{vals[1]:15.5e}"
                + f"{vals[2]:15.5e}{vals[3]:15.5e} ;\n"
            )
        file.write(parspace + "end c2_def;\n")


def load_ind(path):
    """Loads a HAWC2S output .ind file as an python dict

    Parameters
    ----------
    path : str or pathlib.Path
        Path for the .ind file

    Returns
    -------
    dict
        each column of the tabular data is an entry in the dict.
        Units are appended at the end.
    """

    # List of names
    names = [
        "s_m",
        "a",
        "ap",
        "flow_angle_rad",
        "aoa_rad",
        "flow_speed_ms",
        "Fx_Nm",
        "Fy_Nm",
        "M_Nmm",
        "UX0_m",
        "UY0_m",
        "UZ0_m",
        "twist_rad",
        "X_AC0_m",
        "Y_AC0_m",
        "Z_AC0_m",
        "Cl",
        "Cd",
        "Cm",
        "CLp0_rad",
        "CDp0_rad",
        "CMp0_rad",
        "F0",
        "F_rad",
        "CL_FS0",
        "CLFS_rad",
        "V_a_ms",
        "V_t_ms",
        "torsion_rad",
        "vx_ms",
        "vy_ms",
        "chord_m",
        "CT",
        "CP",
        "angle_rad",
        "v_1",
        "v_2",
        "v_3",
    ]
    # Read data into 2D array
    data = np.loadtxt(path, skiprows=1)
    # Split 2D array into a dict
    return {name: val for name, val in zip(names, data.T)}


def load_inds(paths):
    """Loads a HAWC2S output .ind file as an python dict

    Parameters
    ----------
    paths : list
        List of str or pathlib.Path for a set of .ind files

    Returns
    -------
    dict
        each column of the tabular data is an entry in the dict.
        The shape of the data is (n_ind, n_paths)
        Units are appended at the end.
    """
    datas = dict()
    # loop over path
    for ipath, path in enumerate(paths):
        # Load data for single path
        data = load_ind(path)
        # if ipath==0 initialize arrays
        if ipath == 0:
            npaths = len(paths)
            for name, val in data.items():
                datas[name] = np.empty((len(val), npaths))
        # Add single path data to datas
        for name, val in data.items():
            datas[name][:, ipath] = val.copy()
    return datas


def load_pwr(path):
    """Loads a HAWC2S output .pwr file as an python dict

    Parameters
    ----------
    path : str or pathlib.Path
        Path for the .ind file

    Returns
    -------
    dict
        each column of the tabular data is an entry in the dict.
        Units are appended at the end.
    """
    # List of names
    names = [
        "V_ms",
        "P_kW",
        "T_kN",
        "Cp",
        "Ct",
        "Pitch_Q_Nm",
        "Flap_M_kNm",
        "Edge_M_kNm",
        "Pitch_deg",
        "Speed_rpm",
        "Tip_x_m",
        "Tip_y_m",
        "Tip_z_m",
        "J_rot_kgm2",
        "J_DT_kgm2",
        "Torsion_rad",
        "Torque_kNm",
    ]
    # Read data into 2D array
    data = np.loadtxt(path, skiprows=1)
    # Split 2D array into a dict
    return {name: val for name, val in zip(names, data.T)}


def load_pc(path, dset=None):
    """Load the HAWC2 PC-file.

    Parameters
    ----------
    path : str or pathlib.Path
           path for PC-file
    dset : int, optional
        extract only a single set (first set is 1) default is to return all sets, by default None

    Returns
    -------
    list
        Each entry is a set which by them self is a list of profiles.
        If only one set is present it only return a list of profiles.
        Each of the entries in the profile list is a dict with keys:

        * **tc** : *float*
        * **aoa_deg** : *np.ndarray*
        * **cl** : *np.ndarray*
        * **cd** : *np.ndarray*
        * **cm** : *np.ndarray*
        * **comment** : *str*
    """
    with open(path, "r") as file:
        pc_data = []
        # Get number of sets (skipping comment for now)
        nset = int(file.readline().strip().split()[0])
        for iset in range(nset):
            # Add empty list for profs
            pc_data.append([])
            # Get number of profiles
            nprof = int(file.readline().strip().split()[0])
            # Loop over nprof
            for iprof in range(nprof):
                # Add empty list with dict
                pc_data[iset].append(dict())
                # Read line (number of polar points, relative thickness, comment)
                line = file.readline().strip().split()
                naoa = int(line[1])
                pc_data[iset][iprof]["tc"] = float(line[2])
                pc_data[iset][iprof]["comment"] = " ".join(line[3:])
                # Read data as 2D table
                data = np.loadtxt(file, max_rows=naoa)
                pc_data[iset][iprof]["aoa_deg"] = data[:, 0]
                pc_data[iset][iprof]["cl"] = data[:, 1]
                pc_data[iset][iprof]["cd"] = data[:, 2]
                pc_data[iset][iprof]["cm"] = data[:, 3]
    if dset is None:
        if len(pc_data) == 1:
            # Return only list of prof elements
            return pc_data[0]
        # Return all sets if there are multiple
        return pc_data
    # Return given set
    return pc_data[dset - 1]


def save_pc(path, pc_data):
    """Save a HAWC2 PC-file.

    Parameters
    ----------
    path : str or pathlib.Path
        path for PC-file
    pc_data : list
        Can be a list of sets each with a list of profiles or just a list of profiles.
        Each of the entries in the profile list is a dict with keys:

        * **tc** : *float*
        * **aoa_deg** : *np.ndarray or list*
        * **cl** : *np.ndarray or list*
        * **cd** : *np.ndarray or list*
        * **cm** : *np.ndarray or list*
        * **comment** : *str, optional*
    """
    # Ensure that pc_data is list of sets with list of profile data
    if isinstance(pc_data, list):
        if isinstance(pc_data[0], list):
            # Data is a list of list
            pass
        elif isinstance(pc_data[0], dict):
            # Data is a list of profile data and a list is added to be a list of lists
            pc_data = [pc_data]
        else:
            raise ValueError(
                """pc_data need to be a list of profile data dict
                (containing keys: tc, aoa_deg, cl, cd, cm)
                or a list of sets each with a list of profile data."""
            )
    else:
        raise ValueError(
            """pc_data need to be a list of profile data dict
                (containing keys: tc, aoa_deg, cl, cd, cm)
                or a list of sets each with a list of profile data."""
        )
    # Open output file
    with open(path, "w") as file:
        # Write the number of sets
        nsets = len(pc_data)
        file.write(f"{nsets}\n")
        # Loop over the sets
        for set in pc_data:
            # Write the number of profiles
            nprof = len(set)
            file.write(f"{nprof}\n")
            # Loop over profs
            for iprof, prof in enumerate(set, 1):
                naoa = len(prof["aoa_deg"])
                file.write(
                    f"{iprof}  {naoa}  {prof['tc']}  {prof.get('comment', '')}\n"
                )
                np.savetxt(
                    file,
                    np.array([prof["aoa_deg"], prof["cl"], prof["cd"], prof["cm"]]).T,
                )


def load_st(path, dset=None, dsubset=None):
    """Load as HAWC2 ST-file

    Parameters
    ----------
    path : str or pathlib.Path
        path for ST-file
    dset : int, optional
        extract only a single set (first set is 1) default is to return all sets, by default None
    dsubset : _type_, optional
        similar to dset, by default None

    Returns
    -------
    list
        Each entry is a set which by them self is a list of subsets.
        Each of the entries in the subset list is a dict with keys:

        * **s** : *np.ndarray*
        * **m** : *np.ndarray*
        * **x_cg** : *np.ndarray*
        * **y_cg** : *np.ndarray*
        * **ri_x** : *np.ndarray*
        * **ri_y** : *np.ndarray*
        * **x_sh** : *np.ndarray*
        * **y_sh** : *np.ndarray*
        * **E** : *np.ndarray*
        * **G** : *np.ndarray*
        * **I_x** : *np.ndarray*
        * **I_y** : *np.ndarray*
        * **I_p** : *np.ndarray*
        * **k_x** : *np.ndarray*
        * **k_y** : *np.ndarray*
        * **A** : *np.ndarray*
        * **pitch** : *np.ndarray*
        * **x_e** : *np.ndarray*
        * **y_e** : *np.ndarray*
    """
    with open(path, "r") as file:
        line = file.readline()
        st_data = []
        while line:
            # Start with # -> add set
            if line and line.strip()[0] == "#":
                st_data.append([])
            # Start with $ -> add subset
            if line and line.strip()[0] == "$":
                st_data[-1].append(dict())
                nst = int(line.strip().split()[1])
                # Read data a 2D array
                data = np.loadtxt(file, max_rows=nst)
                # Adding data to dict
                for iname, name in enumerate(_ST_NAMES):
                    st_data[-1][-1][name] = data[:, iname]
            # Read next line
            line = file.readline()

    if dset is None:
        if dsubset is None:
            return st_data
        return st_data[:][dsubset]
    st_data = st_data[dset]
    if dsubset is None:
        return st_data
    return st_data[dsubset]


def save_st(path, st_data):
    """Save a HAWC2 ST-file.

    Parameters
    ----------
    path : str or pathlib.Path
        path for PC-file
    st_data : list
        Can be a list of sets each with a list of subset or list of subsets.
        Each of the entries in the subset list is a dict with keys:

        * **s** : *np.ndarray*
        * **m** : *np.ndarray*
        * **x_cg** : *np.ndarray*
        * **y_cg** : *np.ndarray*
        * **ri_x** : *np.ndarray*
        * **ri_y** : *np.ndarray*
        * **x_sh** : *np.ndarray*
        * **y_sh** : *np.ndarray*
        * **E** : *np.ndarray*
        * **G** : *np.ndarray*
        * **I_x** : *np.ndarray*
        * **I_y** : *np.ndarray*
        * **I_p** : *np.ndarray*
        * **k_x** : *np.ndarray*
        * **k_y** : *np.ndarray*
        * **A** : *np.ndarray*
        * **pitch** : *np.ndarray*
        * **x_e** : *np.ndarray*
        * **y_e** : *np.ndarray*
    """
    # Ensure that pc_data is list of sets with list of profile data
    if isinstance(st_data, list):
        if isinstance(st_data[0], list):
            # Data is a list of list
            pass
        elif isinstance(st_data[0], dict):
            # Data is a list of subsets and a list is added to be a list of lists
            st_data = [st_data]
        else:
            raise ValueError(
                """st_data need to be a list of dicts
                (containing keys: %s)
                or a list of sets each with a list subset data."""
                % (_ST_NAMES)
            )
    elif isinstance(st_data, dict):
        # Data is a single subset and is wrapped in two lists
        st_data = [[st_data]]
    else:
        raise ValueError(
            """st_data need to be a list of dicts
                (containing keys: %s)
                or a list of sets each with a list subset data."""
            % (_ST_NAMES)
        )

    # Open output file
    with open(path, "w") as file:
        # Write the number of sets
        nsets = len(st_data)
        file.write(f"{nsets} number of sets\n")
        # Loop over the sets
        for iset, set in enumerate(st_data, 1):
            # Write the set number
            file.write(f"#{iset}\n")
            # Loop over subsets
            for isubset, subset in enumerate(set, 1):
                nst = len(subset["s"])  # length of subset
                file.write(f"${isubset}  {nst}\n")  # write subset number and length
                data = np.array([subset[name] for name in _ST_NAMES])  # create 2D array
                np.savetxt(file, data.T)  # write 2D data


def load_oper(path):
    """Load HAWC2S operational data file

    Parameters
    ----------
    path : str or pathlib.Path
        path for operational data file

    Returns
    -------
    dict
        contain the following keys:

        * **ws_ms** : *ndarray*
        * **pitch_deg** : *ndarray*
        * **rotor_speed_rpm** : *ndarray*
        * **power_kw** : *ndarray (if present)*
        * **thrust_kn** : *ndarray (if present)*
    """
    # Load data as 2D array
    data = np.loadtxt(path, skiprows=1)
    # Ensure data is 2D
    if len(data.shape) == 1:
        data = np.array([data])
    # Return data as dict
    return {name: val for name, val in zip(_OPER_NAMES, data.T)}


def save_oper(path, oper_data):
    """Save an operational data file

    Parameters
    ----------
    path : _type_
        _description_
    oper_data : dict
        With the following keys:

        * **ws_ms** : *ndarray*
        * **pitch_deg** : *ndarray*
        * **rotor_speed_rpm** : *ndarray*
        * **power_kw** : *ndarray (if present)*
        * **thrust_kn** : *ndarray (if present)*
    """
    noper = len(oper_data["ws_ms"])
    with open(path, "w") as file:
        file.write(f"{noper}  wind speed [m/s]  pitch [deg]  rot. speed [rpm]")
        if "power_kw" in oper_data:
            file.write("  power [kW]  thrust [kN]\n")
            data = [oper_data[name] for name in _OPER_NAMES]
        else:
            file.write("\n")
            data = [oper_data[name] for name in _OPER_NAMES[:-2]]
        np.savetxt(file, np.array(data).T)


def load_ctrl_txt(path):
    """Load control parameters from HAWC2S output txt.

    This code is ugly and there is not much to do about it. :)

    Args:
        path (str, pathlib.Path): Path to _ctrl_tuning.txt.

    Returns:
        dict: Dictionary of controller parameters.
    """
    num_tab_skip = 17  # no. lines to skip for table in ctrl.txt
    path = Path(path)  # sanitize inputs
    ctrl_dict = {}  # initialize dictionary
    # open and load parameters up to (not incl.) table
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()  # load contents of file
        # load values line by line (hard-coded, ewwww)
        ctrl_dict["K_Nm/(rad/s)^2"] = float(lines[1].split()[2])
        ctrl_dict["Irotor_kg*m^2"] = float(lines[3].split()[2])
        ctrl_dict["KpTrq_Nm/(rad/s)"] = float(lines[4].split()[2])
        ctrl_dict["KiTrq_Nm/rad"] = float(lines[5].split()[2])
        ctrl_dict["KpPit_rad/(rad/s)"] = float(lines[7].split()[2])
        ctrl_dict["KiPit_rad/rad"] = float(lines[8].split()[2])
        ctrl_dict["K1_deg"] = float(lines[9].split()[2])
        ctrl_dict["K2_deg^2"] = float(lines[9].split()[6])
        ctrl_dict["Kp2_rad/(rad/s)"] = float(lines[11].split()[2])
        ctrl_dict["Ko1_deg"] = float(lines[12].split()[2])
        ctrl_dict["Ko2_deg^2"] = float(lines[12].split()[6])

    # load the table using numpy, convert to pandas
    aero_gains = np.loadtxt(path, skiprows=num_tab_skip)
    aero_gains_df = pd.DataFrame(aero_gains, columns=_AERO_GAIN_NAMES)
    aero_gains_df.set_index("theta_deg", inplace=True)
    ctrl_dict["aero_gains"] = aero_gains_df

    return ctrl_dict


class ReadHAWC2(object):
    """Read a HAWC2 time-marching simulation into an object.

    Usage
    ------
    >>> h2res = ReadHAWC2(fname, loaddata=False)


    Parameters
    ----------
    fname : pathlib.Path or str
        Path to file to load. Currently only GTSDF (HDF5) format is supported.
    loaddata : boolean
        Whether to load the data itself (True) or just the metadata (False). Default is
        True.
    """

    def __init__(self, fname, loaddata=True):
        """Initialize the object. Sanitize inputs and call subsequent method."""
        # sanitize inputs and initialize variables
        fname = Path(fname)
        self.fname = fname
        self.data = None
        self.chaninfo = None
        self.nrch = None
        self.nrsc = None
        self.freq = None
        self.fformat = None
        self.t = None
        # self.Iknown = []  # to keep track of what has been read all ready

        # check if file exists and file extension given
        if not fname.is_file():
            raise OSError(
                f'File "{fname.as_posix()}" is not found! '
                + "Verify the path is correct."
            )

        # call different readers for different types of files
        if ".hdf5" in fname.suffix:
            self._read_gtsdf(loaddata=loaddata)
        elif ".sel" in fname.suffix:
            warnings.warn("Reading sel files is not yet implemented! Sorry. :(")
        elif ".dat" in fname.suffix:
            warnings.warn("Reading dat files is not yet implemented! Sorry. :(")
        elif ".int" in fname.suffix:
            warnings.warn("Reading int files is not yet implemented! Sorry. :(")
        else:
            raise ValueError(
                f'File extension "{fname.suffix}" is unknown!'
                + " Please see function documentation."
            )

    def _read_gtsdf(self, loaddata=True):
        """Read HAWC2 file format gtsdf. Assign default attributes plus
        gtsdf_description."""
        self.t, data, info = gtsdf.load(self.fname)
        self.chaninfo = [
            ["Time"] + info["attribute_names"],
            ["s"] + info["attribute_units"],
            ["Time"] + info["attribute_descriptions"],
        ]
        self.nrch = data.shape[1] + 1
        self.nrsc = data.shape[0]
        self.freq = self.nrsc / self.t
        self.fformat = "GTSDF"
        self.gtsdf_description = info["description"]
        if loaddata:
            self.data = np.hstack([self.t[:, np.newaxis], data])


class HAWC2Stats(pd.DataFrame):
    """A DataFrame-like object for maniuplating HAWC2 statistics files.

    Additions are the `statspath` attribute and the `filter_channel()` method.
    """

    # add the statspath attribute to the DataFrame attributes
    _metadata = ["statspath"]

    # return the same object if we slice
    @property
    def _constructor(self):
        return HAWC2Stats

    def filter_channel(self, chan_id, chan_desc_dict):
        """Isolate data for a channel based on the text in the 'Description' columnn.

        Each channel in a HAWC2 time-series output files has a name, units, and description.
        This method searches through the lowercase descriptions to find the first channel that
        contains the provided pattern. The pattern is given by the values in chan_desc_dict.
        Each key in chan_desc_dict is a channel identifier, and the value is some expected
        pattern in the description for that channel. E.g., the value for the identifier "GenTrq"
        might be "mgen lss".

        Args:
            chan_id (str): Identifier of channel to isolate. E.g., 'BldPit'. Must be a key
                in chan_desc_dict.
            chan_desc_dict (dict): Mapping from channel identifiers to pattern to search for
                in the channel descriptions.

        Returns:
            lacbox.io.HAWC2Stats: Filtered HAWC2Stats object for requested channel.
        """
        # throw error if requested channel is not in dictionary
        if chan_id not in chan_desc_dict.keys():
            raise ValueError(f'Identifier "{chan_id}" not in chan_descs dict!')
        # find the rows whose lowercase description match the value in the dictionary
        desc = chan_desc_dict[chan_id]
        matching_rows = self.desc.apply(lambda s: desc in str(s).lower())
        # find the first non-zero element and convert to hawc2-equivalent channel index
        chan_idx = np.argmax(matching_rows) + 1
        return self[self.ichan == chan_idx]


def load_stats(path, subfolder=None, statstype=None):
    """Load a HDF5 stats file into a HAWC2Stats object.

    Parameters
    ----------
    path (str, pathlib.Path): Path to stats file to load. Can be HDF5 or CSV.
    subfolder (str, optional): Option to only return data for a single subfolder.
        Default is None, all data loaded.
    statstype (str, optional): Whether filename patterns match the steady or
        turbulent pattern. Used in identifying wind speeds. Defaults to 'steady'.

    Returns:
    --------
    lacbox.io.HAWC2Stats: Loaded statstics
    np.array or None: Unique wind speeds in the dataset identified from filesnames.
        None if statstype not given.
    """
    path = Path(path)  # sanitize

    # load the stats file and add the absolute path as an attribute
    if path.suffix.lower() == ".hdf5":
        h2stats = HAWC2Stats(pd.read_hdf(path, "stats_df"))
    elif path.suffix.lower() == ".csv":
        h2stats = HAWC2Stats(pd.read_csv(path, index_col=0))
    else:
        raise ValueError("Sorry! I can only load HDF5 and CSV files!")
    h2stats.statspath = Path(path).absolute()

    # filter by subfolder if requested
    if subfolder is not None:
        h2stats = h2stats[h2stats.subfolder == subfolder]

    # determine function to get wsp from filename based on steady or turb
    if statstype == "steady":
        wspfun = lambda s: float(s.split("_")[-1].rstrip(".hdf5"))
    elif statstype == "turb":
        wspfun = lambda s: float(s.split("_")[-2])
    elif statstype is None:
        wspfun = None
    else:
        raise ValueError(f'Unknown statstype "{statstype}"!')

    # make a column of wind speeds and save unique values
    if wspfun is not None:
        h2stats.loc[:, "wsp"] = h2stats.filename.apply(wspfun)
        wsps = np.sort(h2stats.wsp.unique())
    else:
        h2stats.loc[:, "wsp"] = None
        wsps = None

    return h2stats, wsps
