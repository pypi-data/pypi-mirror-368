import audiotoolbox as audio
import numpy as np
import numpy.testing as testing


def test_rms():
    sig = audio.Signal(2, 100e-3, 100e3)
    sig.add_tone(100)
    rms = sig.stats.rms
    testing.assert_allclose(rms, 1.0 / np.sqrt(2))


def test_mean():
    sig = audio.Signal((2, 2), 1, 48000)
    assert sig.stats.mean.shape == sig.n_channels
    assert np.all(sig.stats.mean == 0)

    sig = audio.Signal((2, 2), 1, 48000)
    sig.ch[0, 1] += 1
    assert sig.stats.mean[0, 1] == 1


def test_var():
    sig = audio.Signal((2, 2), 1, 48000)
    assert sig.stats.var.shape == sig.n_channels
    assert np.all(sig.stats.var == 0)

    sig = audio.Signal((2, 2), 1, 48000).add_noise()
    sig *= np.sqrt(2)
    assert sig.stats.var.shape == sig.n_channels
    testing.assert_allclose(sig.stats.var, 2)


def test_dbspl():
    sig = audio.Signal((2, 2), 1, 48000).add_noise()
    sig *= np.sqrt(2)
    dbspl = audio.calc_dbspl(sig)
    testing.assert_array_almost_equal(sig.stats.dbspl, dbspl)


def test_dbfs():
    sig = audio.Signal((2, 2), 1, 48000).add_noise()
    sig *= np.sqrt(2)
    dbspl = audio.calc_dbfs(sig)
    testing.assert_array_almost_equal(sig.stats.dbfs, dbspl)
    assert sig.stats.dbfs.shape == (2, 2)


def test_crest_factor():
    sig = audio.Signal((2, 2), 1, 48000).add_noise()
    sig *= np.sqrt(2)
    comp_val = audio.crest_factor(sig)
    testing.assert_array_almost_equal(sig.stats.crest_factor, comp_val)


def test_dba():
    sig = audio.Signal(1, 1, 48000).add_tone(1000)
    sig.set_dbspl(70)
    assert np.abs(sig.stats.dba - 70) < 0.2

    sig = audio.Signal(1, 1, 48000).add_noise()
    dba = sig.stats.dba
    siga = audio.filter.a_weighting(sig)
    dba2 = siga.stats.dbspl
    assert dba == dba2


def test_dbc():
    sig = audio.Signal(1, 1, 48000).add_tone(1000).add_fade_window(30e-3)
    sig.set_dbspl(70)
    assert np.abs(sig.stats.dba - 70) < 0.2

    sig = audio.Signal(1, 1, 48000).add_noise().add_fade_window(30e-3)
    dba = sig.stats.dba
    siga = audio.filter.a_weighting(sig)
    dba2 = siga.stats.dbspl
    assert dba == dba2


def test_octave_band_levels():
    sig = audio.Signal(1, 10, 48000).add_noise("pink").set_dbfs(-10)

    fc2, dbfs2 = sig.stats.octave_band_levels(oct_fraction=1)
    assert fc2.shape == dbfs2.shape
    assert fc2.size == dbfs2.size
    bank = audio.filter.bank.octave_bank(sig.fs, oct_fraction=1)
    bank_out = bank.filt(sig)
    testing.assert_array_almost_equal(dbfs2, bank_out.stats.dbfs)

    fc3, dbfs3 = sig.stats.octave_band_levels(oct_fraction=3)
    assert fc3.shape == dbfs3.shape
    assert fc3.size == dbfs3.size
    bank = audio.filter.bank.octave_bank(sig.fs, oct_fraction=3)
    bank_out = bank.filt(sig)
    testing.assert_array_almost_equal(dbfs3, bank_out.stats.dbfs)

    sig2 = audio.Signal((2, 3), 10, 48000).add_noise("pink").set_dbfs(-10)
    fc2, dbfs2 = sig2.stats.octave_band_levels(oct_fraction=1)
    assert fc2.shape[0] == dbfs2.shape[-1]
    bank = audio.filter.bank.octave_bank(sig2.fs, oct_fraction=1)
    bank_out = bank.filt(sig2)
    testing.assert_array_almost_equal(dbfs2, bank_out.stats.dbfs)

    sig2 = audio.Signal((2, 3), 10, 48000).add_noise("pink").set_dbfs(-10)
    fc2, dbfs2 = sig2.stats.octave_band_levels(oct_fraction=1)
    assert sig2.n_channels == dbfs2.shape[:-1]
