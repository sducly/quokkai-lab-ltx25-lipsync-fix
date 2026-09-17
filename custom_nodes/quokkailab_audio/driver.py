"""Unchanged ringmod70 numerical recipe; mono PCM speech in, PCM24 WAV out."""
import io


def wav_bytes(samples, rate):
    import soundfile as sf
    buffer = io.BytesIO()
    sf.write(buffer, samples, rate, format='WAV', subtype='PCM_24')
    return buffer.getvalue()


def make_driver(clean):
    """Apply the validated ringmod70 recipe, preserving the exact timeline."""
    import numpy as np
    import soundfile as sf
    from scipy.signal import butter, sosfiltfilt
    x, sr = sf.read(clean, dtype='float64', always_2d=True)
    if x.shape[1] != 1 or not len(x) or not np.isfinite(x).all():
        raise ValueError('Expected nonempty, finite mono speech.')
    active = np.flatnonzero(np.mean(np.abs(x), axis=1) > .01)
    if not len(active):
        raise ValueError('No speech detected above -40 dBFS.')
    t = np.arange(len(x), dtype=np.float64) / sr
    y = x * (0.55 + 0.45 * np.cos(2 * np.pi * 70 * t))[:, None]
    y = sosfiltfilt(butter(2, [180, 6500], btype='bandpass', fs=sr, output='sos'), y, axis=0)
    peak = float(np.max(np.abs(y)))
    if peak:
        y *= 0.95 / peak
    y[:active[0] + 1] = x[:active[0] + 1]
    y[active[-1]:] = x[active[-1]:]
    y[x == 0] = 0
    if not np.isfinite(y).all() or np.max(np.abs(y)) >= 1:
        raise ValueError('Invalid conditioning audio.')
    data = wav_bytes(y, sr)
    y, rate = sf.read(io.BytesIO(data), dtype='float64', always_2d=True)
    crossings = np.flatnonzero(np.mean(np.abs(y), axis=1) > .01)
    if rate != sr or y.shape != x.shape or not np.isfinite(y).all() or np.max(np.abs(y)) >= 1 or not np.array_equal(crossings[[0,-1]], active[[0,-1]]):
        raise ValueError('Conditioning audio violates timing invariants.')
    return data
