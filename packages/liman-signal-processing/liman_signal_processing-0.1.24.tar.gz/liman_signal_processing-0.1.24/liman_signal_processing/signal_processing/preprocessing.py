import numpy as np
from scipy import signal


def filter_signal(data, cutoff_freq, sampling_rate, filter_type='lowpass'):
    """
    Фильтрация сигнала.

    :param data: Входной сигнал (numpy array).
    :param cutoff_freq: Частота среза (одна частота для lowpass/highpass, кортеж (lowcut, highcut) для bandpass).
    :param sampling_rate: Частота дискретизации.
    :param filter_type: Тип фильтра ('lowpass', 'highpass', 'bandpass').
    :return: Отфильтрованный сигнал.
    """
    nyquist_freq = 0.5 * sampling_rate

    if filter_type == 'bandpass':
        # Для полосового фильтра cutoff_freq должен быть кортежем (lowcut, highcut)
        lowcut, highcut = cutoff_freq
        normal_cutoff = [lowcut / nyquist_freq, highcut / nyquist_freq]
    else:
        # Для lowpass/highpass cutoff_freq — это одна частота
        normal_cutoff = cutoff_freq / nyquist_freq

    # Создаем фильтр
    b, a = signal.butter(4, normal_cutoff, btype=filter_type)
    filtered_data = signal.filtfilt(b, a, data)
    return filtered_data

def apply_window(data, window_type='hann'):
    """
    Накладывает оконную функцию на сигнал.

    :param data: Входной сигнал.
    :param window_type: Тип окна ('hann', 'hamming', 'blackman').
    :return: Сигнал с наложенным окном.
    """
    if window_type == 'hann':
        window = np.hanning(len(data))
    elif window_type == 'hamming':
        window = np.hamming(len(data))
    elif window_type == 'blackman':
        window = np.blackman(len(data))
    else:
        raise ValueError("Неизвестный тип окна")

    return data * window