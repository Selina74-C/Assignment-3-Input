# tools/realtime_plot.py
import soundfile as sf
#!/usr/bin/env python3
"""Realtime waveform player + smoothed display (wavtopng.py)

Plays `romantic.wav` and shows a realtime waveform. Audio is passed
through a light exponential low-pass filter to reduce high-frequency
harshness; the displayed waveform is lightly smoothed with a moving
average to make the visualization calmer.
"""

import soundfile as sf
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import sys


wav = 'romantic.wav'  # path (update if needed)
data, sr = sf.read(wav)
if data.ndim > 1:
    data = data.mean(axis=1)  # mix to mono

# Playback / buffer parameters
blocksize = 1024
buffer_seconds = 8
buffer_len = int(buffer_seconds * sr)
buf = deque(np.zeros(buffer_len, dtype=np.float32), maxlen=buffer_len)

# Smoothing (exponential low-pass) parameters
# cutoff frequency in Hz for audio smoothing (lower = smoother)
cutoff_hz = 6000.0
dt = 1.0 / sr
rc = 1.0 / (2 * np.pi * cutoff_hz)
alpha = dt / (rc + dt)
prev_sample = 0.0

pos = 0

def smooth_chunk(chunk):
    """Apply exponential smoothing to a 1-D numpy chunk in-place.
    Uses a simple recursive filter y[n] = alpha * x[n] + (1-alpha) * y[n-1]
    and preserves state across calls via the enclosing prev_sample.
    """
    global prev_sample
    out = np.empty_like(chunk)
    y_prev = prev_sample
    a = alpha
    one_minus_a = 1.0 - a
    for i, x in enumerate(chunk):
        y = a * x + one_minus_a * y_prev
        out[i] = y
        y_prev = y
    prev_sample = y_prev
    return out


def callback(outdata, frames, time, status):
    global pos
    if status:
        print(status, file=sys.stderr)
    chunk = np.zeros(frames, dtype=np.float32)
    if pos < len(data):
        read = min(frames, len(data) - pos)
        chunk[:read] = data[pos:pos+read]
        pos += read
    # apply smoothing to the chunk
    chunk_sm = smooth_chunk(chunk)
    outdata[:] = np.reshape(chunk_sm, (frames, 1))
    # append to buffer for plotting
    for v in chunk_sm:
        buf.append(v)


def main():
    # Start playback stream
    stream = sd.OutputStream(channels=1, samplerate=sr, blocksize=blocksize, callback=callback)
    stream.start()

    # Setup Matplotlib live plot
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 3))
    x = np.linspace(-buffer_seconds, 0, buffer_len)
    line, = ax.plot(x, np.zeros(buffer_len), color='#66c2ff', linewidth=1.2)
    ax.set_ylim(-1.0, 1.0)
    ax.set_xlim(-buffer_seconds, 0)
    ax.set_xlabel('seconds')
    ax.set_ylabel('amplitude')
    ax.set_title('Realtime waveform - romantic.wav (smoothed)')

    def update(frame):
        arr = np.array(buf)
        # light moving-average smoothing for display
        window = 5
        if len(arr) >= window:
            kernel = np.ones(window) / window
            arr_sm = np.convolve(arr, kernel, mode='same')
        else:
            arr_sm = arr
        line.set_ydata(arr_sm)
        return line,

    ani = FuncAnimation(fig, update, interval=50, blit=True)
    try:
        plt.show()
    finally:
        # ensure stream is closed when window closes
        try:
            stream.stop()
            stream.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
