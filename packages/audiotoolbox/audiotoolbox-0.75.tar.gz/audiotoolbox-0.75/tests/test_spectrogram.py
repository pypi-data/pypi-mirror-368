import audiotoolbox as audio
from scipy.signal import spectrogram
from scipy.signal.windows import get_window
import numpy as np
import matplotlib.pyplot as plt

win = "hann"

sig = audio.Signal(1, 1, 48000)
sig.add_tone(500).set_dbfs(0)
sig.add_noise("pink")
sig.add_fade_window(10e-3)


spec, fc = sig.time_frequency.gammatone_specgram(
    nperseg=1024, noverlap=512, flow=16, fhigh=16000, step=1 / 3
)
print(spec.max())
fig, ax = plt.subplots(1, 1)
cb = ax.pcolormesh(spec.time, fc, spec.T)
ax.set_yscale("log")
ax.set_ylim(16, 16000)
ax.set_ylabel("Frequency / Hz")
ax.set_xlabel("Time / s")
cb = plt.colorbar(cb, ax=ax)
cb.set_label("dB FS")


spec, fc = sig.time_frequency.stft_specgram(nperseg=1024, noverlap=512)
print(spec.max())
fig, ax = plt.subplots(1, 1)
cb = ax.pcolormesh(spec.time, fc, spec.T)
ax.set_yscale("log")
ax.set_ylim(16, 16000)
ax.set_ylabel("Frequency / Hz")
ax.set_xlabel("Time / s")
cb = plt.colorbar(cb, ax=ax)
cb.set_label("dB FS")
