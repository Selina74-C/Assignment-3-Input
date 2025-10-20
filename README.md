
# Assignment-3-Input

This repository contains generated music (jazz/romantic/classical) and visualizers.

## Jazz MIDI generator

This small project generates a short 12-bar blues MIDI file and provides a lead-sheet in ABC notation.

Files created:

- `generate_jazz.py` - Python script that produces `jazz.mid` using `mido`.
- `lead_sheet.abc` - ABC notation lead-sheet for the melody.
- `requirements.txt` - dependencies for running the script.

How to run (macOS / zsh):

1. Create a virtualenv and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the generator:

```bash
python generate_jazz.py
```

This will write `jazz.mid` in the same directory. You can open it with a DAW or a MIDI player. To convert the ABC file to sheet music, use `abcm2ps` or an online ABC renderer.

## Interactive generative artwork

The repository includes a Pygame-based interactive visual that reacts to audio:

- `tools/interactive_art.py` — Pygame app that plays `visual_garden/romantic_smooth.wav` (preferred) or `romantic.wav` (fallback). It reads audio in a background thread and renders audio-reactive particles. Use the on-screen sliders for sensitivity and smoothing.
- `tools/interactive_art_clean.py` — a verified reference copy kept for testing and debugging.
- `tools/run_interactive.py` — small CLI wrapper that starts the interactive app and optionally spawns ffmpeg to record the screen and audio.

Examples:

```bash
# run for 10 seconds without recording
python tools/run_interactive.py --duration 10

# run and record (requires ffmpeg available on PATH, may need to adapt ffmpeg args per OS)
python tools/run_interactive.py --duration 10 --record out.webm
```

### Recording notes

- The `--record` option uses `ffmpeg` and the macOS `avfoundation` input in the default implementation inside `tools/interactive_art.py::maybe_start_rec`.
- If you're on Linux or Windows you'll need to modify the ffmpeg command to match your platform (for example, `x11grab` on Linux or `gdigrab` on Windows).
- The wrapper will attempt to start ffmpeg and will terminate it when the interactive session ends.

### Running locally

1. Activate your Python virtualenv (project uses `.venv`):

```bash
source .venv/bin/activate
```

2. Install dependencies if not present (pygame, numpy, sounddevice, soundfile):

```bash
pip install pygame numpy sounddevice soundfile
```

3. Run the interactive art (the script will check for `visual_garden/romantic_smooth.wav` or `romantic.wav`):

```bash
python tools/run_interactive.py --duration 15
```

If you'd like, I can adapt the ffmpeg recording flags for your OS and run a headless smoke test recording (no GUI) or run a live graphical smoke test if you confirm it's OK to open a window in this session.
