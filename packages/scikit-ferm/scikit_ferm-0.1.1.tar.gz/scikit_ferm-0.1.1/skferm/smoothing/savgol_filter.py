import numpy as np
from scipy.signal import savgol_filter


def savitzky_golay(data, time=None, window_size=4, poly_order=2):
    """
    Apply Savitzky-Golay smoothing and return an interpolator.

    Parameters
    ----------
    data : np.ndarray
        1D array of data to smooth.
    time : np.ndarray, optional
        1D array of time points. If None, indices are used.
    window_length : int, default=5
        Length of the filter window.
    poly_order : int, default=2
        Order of the polynomial used to fit the samples.

    Returns
    -------
    interpolator
        Interpolation function for the smoothed data.
    """
    if time is None:
        time = np.arange(len(data))

    # Apply Savitzky-Golay filter
    smoothed = savgol_filter(data, window_size, poly_order)

    # Create an interpolator function using np.interp
    def interpolator(x):
        return np.interp(x, time, smoothed)

    return smoothed, interpolator
