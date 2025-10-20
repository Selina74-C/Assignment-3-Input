"""Small CLI wrapper to run the interactive art with sensible defaults.

Usage examples:
  python tools/run_interactive.py --duration 10
  python tools/run_interactive.py --duration 15 --record out.webm
"""

import argparse
import pathlib
import subprocess

from tools import interactive_art


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--duration', type=float, default=None)
    p.add_argument('--record', type=pathlib.Path, default=None, help='Optional output path for ffmpeg recording (e.g. out.webm)')
    args = p.parse_args()

    rec_proc = None
    try:
        rec_proc = interactive_art.maybe_start_rec(args.record)
        interactive_art.main(duration=args.duration)
    finally:
        if rec_proc:
            rec_proc.terminate()
            rec_proc.wait()


if __name__ == '__main__':
    main()
