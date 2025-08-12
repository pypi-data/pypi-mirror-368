import audiotoolbox as audio
import IPython.display as ipd
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal

sig = np.random.randn(48000, 1)
b, a = signal.butter(1, 10, "low", fs=48000)
sig_out1 = signal.lfilter(b, a, sig, axis=0)
sig_out2 = signal.lfilter(b, a, sig.squeeze())

np.testing.assert_almost_equal(sig_out1.squeeze(), sig_out2)

# sig = (
#     audio.Signal(1, 10, 48000)
#     .add_noise("pink")
#     .bandpass(5000, 500, "butter")
#     .set_dbfs(-10)
# )
# bank = audio.filter.bank.octave_bank(sig.fs, fhigh=10079, oct_fraction=3)
# bank_out = bank.filt(sig.ch[0])
# fig, ax = plt.subplots(1, 1)
# dbvals = bank_out.stats.dbfs
# low = dbvals.min() * 1.1
# ax.bar(bank.fc, dbvals - low, bottom=low, width=bank.bw, ec="k")
# ax.set_xscale("log")
# ax.set_ylabel("FS Level / dB")
# ax.set_xlabel("Frequency / Hz")
# ax.set_title("1/3 octave Band Levels")


# bank2 = audio.filter.bank.octave_bank(sig.fs, fhigh=10079, oct_fraction=1)
# bank2_out = bank2.filt(sig.ch[0])
# fig, ax = plt.subplots(1, 1)
# dbvals = bank2_out.stats.dbfs
# low = dbvals.min() * 1.1
# ax.bar(bank2.fc, dbvals - low, bottom=low, width=bank2.bw, ec="k")
# ax.set_xscale("log")
# ax.set_ylabel("FS Level / dB")
# ax.set_xlabel("Frequency / Hz")
# ax.set_title("1/3 octave Band Levels")

# bank2 = audio.filter.bank.octave_bank(sig.fs, oct_fraction=1)
# flow = bank2.fc - bank2.bw / 2
# fhigh = bank2.fc + bank2.bw / 2
# plt.plot(flow[1::], "o")
# plt.plot((bank2.fc + bank2.bw / 2), "o")


# flow = bank.fc - bank.bw / 2
# fhigh = bank.fc - bank.bw / 2
