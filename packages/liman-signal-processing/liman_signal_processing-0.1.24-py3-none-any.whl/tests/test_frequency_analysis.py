import numpy as np
from liman_signal_processing.signal_processing.frequency_analysis import compute_amplitude_spectrum

def test_compute_fft():
    # Создаем тестовый сигнал
    sampling_rate = 1000
    t = np.linspace(0, 1, sampling_rate, endpoint=False)
    signal = np.sin(2 * np.pi * 50 * t)  # Сигнал с частотой 50 Гц

    # Вычисляем спектр
    frequencies, spectrum = compute_amplitude_spectrum(signal, sampling_rate, (10, 1000))

    # Проверяем, что пик спектра находится на частоте 50 Гц
    dominant_frequency = frequencies[np.argmax(spectrum)]
    assert np.isclose(dominant_frequency, 50, atol=1), "Ошибка в расчете спектра"