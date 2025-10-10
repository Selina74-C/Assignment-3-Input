# Jazz MIDI generator

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
