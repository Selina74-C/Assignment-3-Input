import numpy as np
import soundfile as sf
from scipy.signal import butter, filtfilt, fftconvolve
from pathlib import Path


def lowpass(x, sr, cutoff=8000, order=4):
    ny = 0.5 * sr
    normal_cutoff = cutoff / ny
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, x)


def make_ir(sr, length_s=0.6, decay=3.0):
    n = int(length_s * sr)
    # noise-based IR with exponential decay
    ir = np.random.normal(0, 1, n)
    t = np.linspace(0, 1, n)
    ir *= np.exp(-decay * t)
    # apply a gentle LP to IR to make reverb smooth
    ir = lowpass(ir, sr, cutoff=6000)
    # normalize
    ir /= np.max(np.abs(ir) + 1e-9)
    return ir


def make_pad(sr, length_s, freqs=[220.0, 277.18, 329.63], amp=0.06):
    # create a slow evolving pad using a few detuned saw/sine harmonics
    t = np.linspace(0, length_s, int(sr * length_s), endpoint=False)
    pad = np.zeros_like(t)
    for i, f in enumerate(freqs):
        detune = 1.0 + (i - 1) * 0.002
        pad += 0.6 * np.sin(2 * np.pi * f * detune * t)
        pad += 0.15 * np.sin(2 * np.pi * f * 2 * detune * t)
    # slow amplitude modulation
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t + 0.1)
    pad *= lfo
    # gentle lowpass
    pad = lowpass(pad, sr, cutoff=1200)
    pad *= amp / (np.max(np.abs(pad) + 1e-9))
    return pad


def fade_in_out(x, sr, fade_s=0.5):
    n = len(x)
    fade_n = int(min(fade_s * sr, n//2))
    if fade_n <= 0:
        return x
    env = np.ones(n)
    env[:fade_n] = np.linspace(0, 1, fade_n)
    env[-fade_n:] = np.linspace(1, 0, fade_n)
    return x * env


def main():
    src = Path('romantic.wav')
    if not src.exists():
        print('romantic.wav not found at', src.resolve())
        return
    y, sr = sf.read(str(src))
    if y.ndim > 1:
        y = y.mean(axis=1)

    print('Loaded', src, 'sr=', sr, 'samples=', len(y))

    # Apply lowpass to smooth harsh highs
    y_lp = lowpass(y, sr, cutoff=9000)

    # Create reverb IR and convolve (mono)
    ir = make_ir(sr, length_s=0.7, decay=3.2)
    wet = fftconvolve(y_lp, ir, mode='full')[:len(y_lp)]

    # Mix dry/wet
    wet_level = 0.28
    y_reverb = (1.0 - wet_level) * y_lp + wet_level * wet

    # Add a subtle pad underneath
    pad = make_pad(sr, len(y_reverb)/sr, freqs=[130.81, 164.81, 196.00], amp=0.05)
    # pad may be shorter/longer; trim or pad
    if len(pad) < len(y_reverb):
        pad = np.pad(pad, (0, len(y_reverb) - len(pad)))
    else:
        pad = pad[:len(y_reverb)]

    out = y_reverb + pad

    # gentle smoothing by another lowpass slightly
    out = lowpass(out, sr, cutoff=12000)

    # fade in/out to avoid clicks
    out = fade_in_out(out, sr, fade_s=0.8)

    # normalize
    peak = np.max(np.abs(out) + 1e-9)
    out = out / peak * 0.95

    out_path = Path('visual_garden/romantic_smooth.wav')
    sf.write(str(out_path), out, sr)
    print('Wrote', out_path)


if __name__ == '__main__':
    main()
