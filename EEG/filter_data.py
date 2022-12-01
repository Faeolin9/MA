import numpy as np
from scipy.signal import iirnotch, filtfilt, butter, sosfilt, firwin, lfilter, cheby2


def filter_data(notch_type: str, filter_type: str, sampling_frequency: float, data: np.ndarray, overt_data: bool) \
        -> np.ndarray:
    """Remove powerline frequency"""
    if notch_type == "iir_notch":
        b, a = iirnotch(w0=50.0, Q=30.0, fs=sampling_frequency)
        filtered_data = filtfilt(b, a, data, axis=-1)
    else:
        butter_sos = butter(N=2, Wn=[48.0, 52.0], btype='bandstop', fs=sampling_frequency, output='sos')
        filtered_data = sosfilt(butter_sos, data, axis=-1)
    """Filter the EEG data afterwards"""
    if filter_type == "maurice":
        """Source: https://ieeexplore.ieee.org/document/9061628"""
        butter_sos = butter(N=4, Wn=1.0, btype='highpass', fs=sampling_frequency, output='sos')
        filtered_data = sosfilt(butter_sos, filtered_data, axis=-1)
        if sampling_frequency == 250:
            # with 250 Hz sfreq Nyquist frequency is 125. 200 would be too large.
            wn = 100.0
        else:
            wn = 200.0
        cheby_sos = cheby2(N=17, rs=60.0, Wn=wn, btype='lowpass', fs=sampling_frequency, output='sos')
        filtered_data = sosfilt(cheby_sos, filtered_data, axis=-1)
        if overt_data:
            """Remove muscle artifacts"""
            butter_sos = butter(N=4, Wn=50.0, btype='lowpass', fs=sampling_frequency, output='sos')
            filtered_data = sosfilt(butter_sos, filtered_data, axis=-1)
    elif filter_type == "a15":
        """Source: https://www.sciencedirect.com/science/article/abs/pii/S1746809420303487"""
        fir_coefficients = firwin(numtaps=21, cutoff=[0.5, 60.0], window='hamming', pass_zero='bandpass',
                                  fs=sampling_frequency)
        filtered_data = lfilter(fir_coefficients, 1, filtered_data, axis=-1)
    return filtered_data
