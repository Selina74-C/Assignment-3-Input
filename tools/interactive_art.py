"""Import-safe shim for the interactive art application.

This file intentionally keeps imports lightweight at module import time
so other tools can import this module without triggering pygame's
initialization or other side-effects.

Exports:
- maybe_start_rec(record_path) -> subprocess.Popen | None
- main(duration=None) -> delegates to tools.interactive_art_clean.main
"""
from typing import Optional
import shutil
import subprocess
import sys


def maybe_start_rec(record_path: Optional[str]):
    """Start an ffmpeg subprocess to record the screen+audio.

    Returns a subprocess.Popen instance or None if recording isn't
    requested or ffmpeg isn't available.
    """
    if not record_path:
        return None
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        return None

    record_path = str(record_path)
    plat = sys.platform
    if plat.startswith('darwin'):
        args = [ffmpeg, '-y', '-f', 'avfoundation', '-framerate', '30', '-i', '1:none', record_path]
    elif plat.startswith('linux'):
        import os

        display = os.environ.get('DISPLAY', ':0.0')
        args = [ffmpeg, '-y', '-f', 'x11grab', '-framerate', '30', '-i', f'{display}', record_path]
    elif plat.startswith('win'):
        args = [ffmpeg, '-y', '-f', 'gdigrab', '-framerate', '30', '-i', 'desktop', record_path]
    else:
        return None

    try:
        p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p
    except Exception:
        return None


def main(duration: Optional[float] = None):
    """Delegate to the canonical interactive implementation.

    Import the heavier implementation lazily so importing this module
    remains side-effect-free.
    """
    from .interactive_art_clean import main as real_main

    return real_main(duration=duration)


__all__ = ["maybe_start_rec", "main"]


