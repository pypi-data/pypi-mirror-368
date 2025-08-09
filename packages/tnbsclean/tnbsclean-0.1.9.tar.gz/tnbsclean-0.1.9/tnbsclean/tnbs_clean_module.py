def remove_stim(y, sfreq, half_win, threshold):
    try:
        spike_idxs = np.where(abs(y) > threshold)[0]
        # 2) convert to times (in seconds)
        spike_times = spike_idxs / sfreq
        # 1) Make a copy of your signal
        y_clean = y.copy().astype(float)

        # 3) Blank out (set to NaN) around each spike
        for idx in spike_idxs:
            start = max(0, idx - half_win)
            end   = min(len(y_clean), idx + half_win)
            y_clean[start:end] = np.nan

        # 4) Interpolate linearly over NaNs
        nans     = np.isnan(y_clean)
        not_nans = ~nans
        y_clean[nans] = np.interp(
            np.flatnonzero(nans),
            np.flatnonzero(not_nans),
            y_clean[not_nans]
        )
    except:
        print('it is likely that this channel is noisy')

    return y_clean


def stim_clean(raw, half_win, threshold):
    data_stim = raw.get_data()
    times = raw.times                      
    sfreq = raw.info['sfreq']
    cleaned_data = []
    for i in range(np.size(data_stim,0)):
        print(f'processing {raw.ch_names[i]}')
        y = data_stim[i, :]  
        y_clean = remove_stim(y, sfreq, half_win, threshold)
        cleaned_data.append(y_clean)

    cleaned_data = np.array(cleaned_data)

    if  raw.get_data().shape == cleaned_data.shape:
        raw._data[: :] = cleaned_data
    else:
        raise ValueError("There is a channel present in your data that is consistently pinning all points. "
                       "Please either remove this channel or consider adjusting your threshold to allow for successful interpolation.")

    return raw
