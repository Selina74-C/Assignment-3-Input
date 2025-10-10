from PIL import Image
import numpy as np
import soundfile as sf
from pathlib import Path

spec_path = Path('visual_garden/matplotlib_music_spec.png')
if not spec_path.exists():
    print('Spec image not found:', spec_path.resolve())
    raise SystemExit(1)

img = Image.open(spec_path).convert('L')
arr = np.array(img).astype(np.float32)
# arr shape: (H, W) where vertical is frequency (top=high)
H, W = arr.shape
print('Loaded spec', W, 'x', H)

duration = 30.0  # seconds
sr = 44100
samples = int(duration * sr)
out = np.zeros(samples, dtype=np.float32)

# map rows to frequencies between 100 Hz and 8000 Hz
fmin, fmax = 100.0, 8000.0
freqs = np.geomspace(fmax, fmin, H)  # top is high freq

time_per_col = duration / W
col_samples = int(time_per_col * sr)

phase = np.zeros(H)
for x in range(W):
    col = arr[:, x] / 255.0  # 0..1 magnitude
    t0 = int(x * col_samples)
    t1 = min(samples, t0 + col_samples)
    t = np.arange(t1 - t0) / sr
    frame = np.zeros(t1 - t0, dtype=np.float32)
    # synthesize limited number of partials per column for speed
    idxs = np.where(col > 0.05)[0]
    if len(idxs) > 60:  # limit to strongest 60 bins
        idxs = idxs[np.argsort(col[idxs])][-60:]
    for i in idxs:
        amp = col[i]
        f = freqs[i]
        # incremental phase to avoid clicks
        p = phase[i]
        frame += amp * np.sin(2 * np.pi * f * t + p)
        phase[i] = (p + 2 * np.pi * f * (t[-1] if len(t) else 0)) % (2*np.pi)
    # apply gentle envelope
    env = np.linspace(0,1,len(frame))
    frame *= env * 0.8
    out[t0:t1] += frame

# normalize
out /= np.max(np.abs(out) + 1e-9)
out *= 0.9

out_path = Path('visual_garden/spec_music.wav')
sf.write(str(out_path), out, sr)
print('Wrote', out_path)
