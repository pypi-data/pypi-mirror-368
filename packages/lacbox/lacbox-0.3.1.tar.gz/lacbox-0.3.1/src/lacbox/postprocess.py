# -*- coding: utf-8 -*-
"""Module for post-processing HAWC2 results.
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from lacbox.io import ReadHAWC2


def process_statistics(res_dir, save_path, calc_del=True,
                       m_vals=(3, 4, 5, 8, 10, 12)):
    """Calculate mean, min, DELs, etc. of all files in a directory.

    TODO: Add long-form descriptions

    Parameters
    ----------
    res_dir : str or pathlib.Path
        Path to top-level folder with HAWC2 results files. Can contain
        nested subfolders.
    save_path : str or pathlib.Path
        Path to the stats file to save. If the filename ends with hdf5, 
        file is saved using `df.to_hdf()`, with table saved under key
        `stats_df`. If path ends with `.csv`, then it is saved as a CSV.
    calc_del : boolean, optional
        Whether to calculate the 10-minute damage equivalent loads, which takes more
        time. The default is True.
    m_vals : iterable, optional
        The values of the Wöhler exponent for which to calculate DELs. Only used if
        `calc_del` is True. The default is `[3, 4, 5, 8, 10, 12]`.

    Returns
    -------
    res_df : pandas.DataFrame
        Dataframe with statistics.
    """
    # sanitize input path objects
    res_dir = Path(res_dir)
    save_path = Path(save_path)
    # define constants: statstics to calculate and columns of output dataframe
    base_stats = ['mean', 'max', 'min', 'std', '1%', '50%', '99%']  # base stats
    stats = base_stats
    if calc_del is True:  # include extra if calculating DELs
        del_stats = ['del' + str(m) for m in m_vals]
        stats = base_stats + del_stats
    else:
        stats = base_stats
    cols = ['path', 'filename', 'subfolder', 'ichan', 'names', 'units', 'desc'] + stats  # columns of stats_df

    # get list of res (hdf5) files in the folder(s)
    res_paths = list(res_dir.rglob('*.hdf5'))
    print(f'\n{len(res_paths)} HAWC2 HDF5 time series to process.\n')
    
    # initialize output dataframe and begin loop over files
    for i, fpath in enumerate(res_paths):
        
        # get the filename and name of subfolder
        fpath = res_paths[i]
        filename = fpath.name
        subfolder = fpath.relative_to(res_dir).parent

        print(f'Processing {i+1}/{len(res_paths)}...')

        # load the data, turn to dataframe so we can use .describe()
        h2res = ReadHAWC2(fpath)
        df = pd.DataFrame(h2res.data)
        ichans = np.arange(df.shape[1]) + 1  # index from 1 to match HAWC2
        names, units, desc = h2res.chaninfo
        
        # initialize our stats dataframe for this file and set filenames, paths, etc.
        new_df = pd.DataFrame(columns=cols, index=ichans-1)
        new_df['path'] = str(fpath)
        new_df['filename'] = filename
        new_df['subfolder'] = str(subfolder)
        new_df['ichan'] = ichans
        new_df['names'] = names
        new_df['units'] = units
        new_df['desc'] = desc

        # assign the base stats
        desc_df = df.describe(percentiles=[0.01, 0.99]).T[base_stats]
        new_df[base_stats] = desc_df

        # calculate 10-minute DELs if requested
        if calc_del:
            neq = 600  # assume 1 Hz equivalent frequency
            for ichan in ichans:
                signal = df.values[:, ichan-1]
                new_df.loc[ichan-1, del_stats] = eq_load(signal, m=m_vals, neq=neq)[0]
        
        # append to large df
        if i == 0:
            stats_df = new_df
        else:
            stats_df = pd.concat((stats_df, new_df), ignore_index=True)

    # fix all datatypes before pickling
    stats_df = stats_df.astype(dict(ichan=int))
    for stat in stats:
        stats_df = stats_df.astype({stat: float})

    if 'hdf5' in save_path.suffix.lower():
        stats_df.to_hdf(save_path, key='stats_df', mode='w')
    elif 'csv' in save_path.suffix.lower():
        stats_df.to_csv(save_path)
    else:
        raise ValueError(f'File extension "{save_path.suffix}" is not allowed!'
                         + ' Only hdf5 or csv.')
    print(f'\nResults saved to file "{str(save_path)}".\n')

    return stats_df


# =======================================================================================
# THESE FUNCTIONS ARE COPY-PASTED FROM THE WIND ENERGY TOOLBOX
# https://gitlab.windenergy.dtu.dk/toolbox/WindEnergyToolbox/-/tree/master/wetb/fatigue_tools


def peak_trough(x, R):  #cpdef np.ndarray[long,ndim=1] peak_trough(np.ndarray[long,ndim=1] x, int R):
    """
    Returns list of local maxima/minima.

    x: 1-dimensional numpy array containing signal
    R: Thresshold (minimum difference between succeeding min and max

    This routine is implemented directly as described in
    "Recommended Practices for Wind Turbine Testing - 3. Fatigue Loads", 2. edition 1990, Appendix A
    """

    BEGIN = 0
    MINZO = 1
    MAXZO = 2
    ENDZO = 3
    S = np.zeros(x.shape[0] + 1, dtype=int)

    L = x.shape[0]
    goto = BEGIN

    while 1:
        if goto == BEGIN:
            trough = x[0]
            peak = x[0]

            i = 0
            p = 1
            f = 0
            while goto == BEGIN:
                i += 1
                if i == L:
                    goto = ENDZO
                    continue
                else:
                    if x[i] > peak:
                        peak = x[i]
                        if peak - trough >= R:
                            S[p] = trough
                            goto = MAXZO
                            continue
                    elif x[i] < trough:
                        trough = x[i]
                        if peak - trough >= R:
                            S[p] = peak
                            goto = MINZO
                            continue

        elif goto == MINZO:
            f = -1

            while goto == MINZO:
                i += 1
                if i == L:
                    goto = ENDZO
                    continue
                else:
                    if x[i] < trough:
                        trough = x[i]
                    else:
                        if x[i] - trough >= R:
                            p += 1
                            S[p] = trough
                            peak = x[i]
                            goto = MAXZO
                            continue
        elif goto == MAXZO:
            f = 1
            while goto == MAXZO:
                i += 1
                if i == L:
                    goto = ENDZO
                    continue
                else:
                    if x[i] > peak:
                        peak = x[i]
                    else:
                        if peak - x[i] >= R:
                            p += 1
                            S[p] = peak
                            trough = x[i]
                            goto = MINZO
                            continue
        elif goto == ENDZO:

            n = p + 1
            if abs(f) == 1:
                if f == 1:
                    S[n] = peak
                else:
                    S[n] = trough
            else:
                S[n] = (trough + peak) / 2
            S = S[1:n + 1]
            return S


def pair_range_amplitude_mean(x):  # cpdef pair_range(np.ndarray[long,ndim=1]  x):
    """
    Returns a list of half-cycle-amplitudes
    x: Peak-Trough sequence (integer list of local minima and maxima)

    This routine is implemented according to
    "Recommended Practices for Wind Turbine Testing - 3. Fatigue Loads", 2. edition 1990, Appendix A
    except that a list of half-cycle-amplitudes are returned instead of a from_level-to_level-matrix
    """

    x = x - np.min(x)
    k = np.max(x)
    n = x.shape[0]
    S = np.zeros(n + 1)
    ampl_mean = []
    A = np.zeros((k + 1, k + 1))
    S[1] = x[0]
    ptr = 1
    p = 1
    q = 1
    f = 0
    # phase 1
    while True:
        p += 1
        q += 1

                # read
        S[p] = x[ptr]
        ptr += 1

        if q == n:
            f = 1
        while p >= 4:
            if (S[p - 2] > S[p - 3] and S[p - 1] >= S[p - 3] and S[p] >= S[p - 2]) \
                or\
                    (S[p - 2] < S[p - 3] and S[p - 1] <= S[p - 3] and S[p] <= S[p - 2]):
                # Extract two intermediate half cycles
                ampl = abs(S[p - 2] - S[p - 1])
                mean = (S[p - 2] + S[p - 1]) / 2
                ampl_mean.append((ampl, mean))
                ampl_mean.append((ampl, mean))

                S[p - 2] = S[p]

                p -= 2
            else:
                break

        if f == 0:
            pass
        else:
            break
    # phase 2
    q = 0
    while True:
        q += 1
        if p == q:
            break
        else:
            ampl = abs(S[q + 1] - S[q])
            mean = (S[q + 1] + S[q]) / 2
            ampl_mean.append((ampl, mean))
    return ampl_mean


def check_signal(signal):
    # check input data validity
    if not type(signal).__name__ == 'ndarray':
        raise TypeError('signal must be ndarray, not: ' + type(signal).__name__)

    elif len(signal.shape) not in (1, 2):
        raise TypeError('signal must be 1D or 2D, not: ' + str(len(signal.shape)))

    if len(signal.shape) == 2:
        if signal.shape[1] > 1:
            raise TypeError('signal must have one column only, not: ' + str(signal.shape[1]))
    if np.min(signal) == np.max(signal):
        raise TypeError("Signal contains no variation")



def rainflow_windap(signal, levels=255., thresshold=(255 / 50)):
    """Windap equivalent rainflow counting


    Calculate the amplitude and mean values of half cycles in signal

    This algorithms used by this routine is implemented directly as described in
    "Recommended Practices for Wind Turbine Testing - 3. Fatigue Loads", 2. edition 1990, Appendix A

    Parameters
    ----------
    Signal : array-like
        The raw signal

    levels : int, optional
        The signal is discretize into this number of levels.
        255 is equivalent to the implementation in Windap

    thresshold : int, optional
        Cycles smaller than this thresshold are ignored
        255/50 is equivalent to the implementation in Windap

    Returns
    -------
    ampl : array-like
        Peak to peak amplitudes of the half cycles

    mean : array-like
        Mean values of the half cycles


    Examples
    --------
    >>> signal = np.array([-2.0, 0.0, 1.0, 0.0, -3.0, 0.0, 5.0, 0.0, -1.0, 0.0, 3.0, 0.0, -4.0, 0.0, 4.0, 0.0, -2.0])
    >>> ampl, mean = rainflow_windap(signal)
    """
    check_signal(signal)
    #type <double> is required by <find_extreme> and <rainflow>
    signal = signal.astype(np.double)
    if np.all(np.isnan(signal)):
        return None
    offset = np.nanmin(signal)
    signal -= offset
    if np.nanmax(signal) > 0:
        gain = np.nanmax(signal) / levels
        signal = signal / gain
        signal = np.round(signal).astype(int)


        # If possible the module is compiled using cython otherwise the python implementation is used


        #Convert to list of local minima/maxima where difference > thresshold
        sig_ext = peak_trough(signal, thresshold)


        #rainflow count
        ampl_mean = pair_range_amplitude_mean(sig_ext)

        ampl_mean = np.array(ampl_mean)
        ampl_mean = np.round(ampl_mean / thresshold) * gain * thresshold
        ampl_mean[:, 1] += offset
        return ampl_mean.T


def eq_load(signals, no_bins=46, m=(3, 4, 6, 8, 10, 12), neq=1, rainflow_func=rainflow_windap):
    """Equivalent load calculation

    Calculate the equivalent loads for a list of Wohler exponent and number of equivalent loads

    Parameters
    ----------
    signals : list of tuples or array_like
        - if list of tuples: list must have format [(sig1_weight, sig1),(sig2_weight, sig1),...] where\n
            - sigx_weight is the weight of signal x\n
            - sigx is signal x\n
        - if array_like: The signal
    no_bins : int, optional
        Number of bins in rainflow count histogram
    m : int, float or array-like, optional
        Wohler exponent (default is [3, 4, 6, 8, 10, 12])
    neq : int, float or array-like, optional
        The equivalent number of load cycles (default is 1, but normally the time duration in seconds is used)
    rainflow_func : {rainflow_windap, rainflow_astm}, optional
        The rainflow counting function to use (default is rainflow_windap)

    Returns
    -------
    eq_loads : array-like
        List of lists of equivalent loads for the corresponding equivalent number(s) and Wohler exponents

    Examples
    --------
    >>> signal = np.array([-2.0, 0.0, 1.0, 0.0, -3.0, 0.0, 5.0, 0.0, -1.0, 0.0, 3.0, 0.0, -4.0, 0.0, 4.0, 0.0, -2.0])
    >>> eq_load(signal, no_bins=50, neq=[1, 17], m=[3, 4, 6], rainflow_func=rainflow_windap)
    [[10.311095426959747, 9.5942535021382174, 9.0789213365013932], # neq = 1, m=[3,4,6]
    [4.010099657859783, 4.7249689509841746, 5.6618639965313005]], # neq = 17, m=[3,4,6]

    eq_load([(.4, signal), (.6, signal)], no_bins=50, neq=[1, 17], m=[3, 4, 6], rainflow_func=rainflow_windap)
    [[10.311095426959747, 9.5942535021382174, 9.0789213365013932], # neq = 1, m=[3,4,6]
    [4.010099657859783, 4.7249689509841746, 5.6618639965313005]], # neq = 17, m=[3,4,6]
    """
    try:
        return eq_load_and_cycles(signals, no_bins, m, neq, rainflow_func)[0]
    except TypeError:
        return [[np.nan] * len(np.atleast_1d(m))] * len(np.atleast_1d(neq))


def cycle_matrix(signals, ampl_bins=10, mean_bins=10, rainflow_func=rainflow_windap):
    """Markow load cycle matrix

    Calculate the Markow load cycle matrix

    Parameters
    ----------
    Signals : array-like or list of tuples
        - if array-like, the raw signal\n
        - if list of tuples, list of (weight, signal), e.g. [(0.1,sig1), (0.8,sig2), (.1,sig3)]\n
    ampl_bins : int or array-like, optional
        if int, Number of amplitude value bins (default is 10)
        if array-like, the bin edges for amplitude
    mean_bins : int or array-like, optional
        if int, Number of mean value bins (default is 10)
        if array-like, the bin edges for mea
    rainflow_func : {rainflow_windap, rainflow_astm}, optional
        The rainflow counting function to use (default is rainflow_windap)

    Returns
    -------
    cycles : ndarray, shape(ampl_bins, mean_bins)
        A bi-dimensional histogram of load cycles(full cycles). Amplitudes are\
        histogrammed along the first dimension and mean values are histogrammed along the second dimension.
    ampl_bin_mean : ndarray, shape(ampl_bins,)
        The average cycle amplitude of the bins
    ampl_edges : ndarray, shape(ampl_bins+1,)
        The amplitude bin edges
    mean_bin_mean : ndarray, shape(ampl_bins,)
        The average cycle mean of the bins
    mean_edges : ndarray, shape(mean_bins+1,)
        The mean bin edges

    Examples
    --------
    >>> signal = np.array([-2.0, 0.0, 1.0, 0.0, -3.0, 0.0, 5.0, 0.0, -1.0, 0.0, 3.0, 0.0, -4.0, 0.0, 4.0, 0.0, -2.0])
    >>> cycles, ampl_bin_mean, ampl_edges, mean_bin_mean, mean_edges = cycle_matrix(signal)
    >>> cycles, ampl_bin_mean, ampl_edges, mean_bin_mean, mean_edges = cycle_matrix([(.4, signal), (.6,signal)])
    """

    if isinstance(signals[0], tuple):
        weights, ampls, means = np.array([(np.zeros_like(ampl)+weight,ampl,mean) for weight, signal in signals for ampl,mean in rainflow_func(signal[:]).T], dtype=np.float64).T
    else:
        ampls, means = rainflow_func(signals[:])
        weights = np.ones_like(ampls)
    if isinstance(ampl_bins, int):
        ampl_bins = np.linspace(0, 1, num=ampl_bins + 1) * ampls[weights>0].max()
    cycles, ampl_edges, mean_edges = np.histogram2d(ampls, means, [ampl_bins, mean_bins], weights=weights)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ampl_bin_sum = np.histogram2d(ampls, means, [ampl_bins, mean_bins], weights=weights * ampls)[0]
        ampl_bin_mean = np.nanmean(ampl_bin_sum / np.where(cycles,cycles,np.nan),1)
        mean_bin_sum = np.histogram2d(ampls, means, [ampl_bins, mean_bins], weights=weights * means)[0]
        mean_bin_mean = np.nanmean(mean_bin_sum / np.where(cycles, cycles, np.nan), 1)
    cycles = cycles / 2  # to get full cycles
    return cycles, ampl_bin_mean, ampl_edges, mean_bin_mean, mean_edges



def eq_load_and_cycles(signals, no_bins=46, m=(3, 4, 6, 8, 10, 12), neq=(10 ** 6, 10 ** 7, 10 ** 8), rainflow_func=rainflow_windap):
    """Calculate combined fatigue equivalent load

    Parameters
    ----------
    signals : list of tuples or array_like
        - if list of tuples: list must have format [(sig1_weight, sig1),(sig2_weight, sig1),...] where\n
            - sigx_weight is the weight of signal x\n
            - sigx is signal x\n
        - if array_like: The signal
    no_bins : int, optional
        Number of bins for rainflow counting
    m : int, float or array-like, optional
        Wohler exponent (default is [3, 4, 6, 8, 10, 12])
    neq : int or array-like, optional
        Equivalent number, default is [10^6, 10^7, 10^8]
    rainflow_func : {rainflow_windap, rainflow_astm}, optional
        The rainflow counting function to use (default is rainflow_windap)

    Returns
    -------
    eq_loads : array-like
        List of lists of equivalent loads for the corresponding equivalent number(s) and Wohler exponents
    cycles : array_like
        2d array with shape = (no_ampl_bins, 1)
    ampl_bin_mean : array_like
        mean amplitude of the bins
    ampl_bin_edges
        Edges of the amplitude bins
    """
    cycles, ampl_bin_mean, ampl_bin_edges, _, _ = cycle_matrix(signals, no_bins, 1, rainflow_func)
    if 0:  #to be similar to windap
        ampl_bin_mean = (ampl_bin_edges[:-1] + ampl_bin_edges[1:]) / 2
    cycles, ampl_bin_mean = cycles.flatten(), ampl_bin_mean.flatten()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        eq_loads = [[((np.nansum(cycles * ampl_bin_mean ** _m) / _neq) ** (1. / _m)) for _m in np.atleast_1d(m)]  for _neq in np.atleast_1d(neq)]
    return eq_loads, cycles, ampl_bin_mean, ampl_bin_edges

