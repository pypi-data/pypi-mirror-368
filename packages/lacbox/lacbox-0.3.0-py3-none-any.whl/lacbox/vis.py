import matplotlib.pyplot as plt


def plot_amp(amp_df, mode_names, wsp, title=None):
    """Visualize modal amplitudes for given wind speed.
    
    Parameters
    ----------
    amp_df : pd.Dataframe
        Dataframe of modal amplitudes, generated using a call to `lacbox.io.load_amp`
    mode_names : list
        Names of mode shapes.
    wsp : int, float
        Wind speed to isolate and plot the modal amplitudes for.
    title : string (optional)
        Optional title to add to axes. Default is `None` (no title).

    Returns
    -------
    fig : plt.figure
        Figure handle.
    ax : plt.axes
        Axes handle.
    """
    
    # filter by wind speed
    df_wsp = amp_df.loc[(amp_df['Wind speed'] == wsp)]
    nmodes = amp_df.loc['mode_number'].unique().size - 1
    assert nmodes == len(mode_names)

    # plot the data
    amp_modes_df = df_wsp.loc[:, df_wsp.columns.map(lambda s: 'phase' not in s)].iloc[:, 1:]
    amp_modes_arr = amp_modes_df.to_numpy().reshape(nmodes, -1)

    modal_comps = amp_modes_df.columns.unique()
    ncomps = len(modal_comps)

    # make plot
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(amp_modes_arr, cmap='OrRd') #, cmap=cmap, norm=norm)

    ax.set(xticks=range(len(modal_comps)),
        yticks=(range(nmodes)),
        yticklabels=[f'Mode {i}' for i in range(1, nmodes+1)] if mode_names is None else mode_names,
        title=title)
    ax.set_xticklabels(modal_comps, rotation=90)

    # make vertical lines separating modes
    for i in range(5):
        ax.plot([(i+1)*3 - 0.5, (i+1)*3 - 0.5], [-0.5, nmodes-0.5],'-', c='0.3')
        ax.plot([(i+1)*3 - 1.5, (i+1)*3 - 1.5], [-0.5, nmodes-0.5],':', c='0.8')
        ax.plot([(i+1)*3 - 2.5, (i+1)*3 - 2.5], [-0.5, nmodes-0.5],':', c='0.8')
    for i in range(nmodes):
        ax.plot([-0.5, ncomps-0.5], [i + 0.5, i + 0.5],':', c='0.8')

    im_ratio = amp_modes_arr.shape[0]/amp_modes_arr.shape[1]
    plt.colorbar(im, fraction=0.047*im_ratio)

    fig.tight_layout()

    return fig, ax
