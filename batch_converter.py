#!/usr/bin/env python3
import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', type=Path, help='Output directory. Defaults to same directory as input file.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose log output')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing output')
    parser.add_argument('files', nargs='+', help='Files to convert')
    args = parser.parse_args()

    return args


def main() -> None:
    args = parse_args()

    for f in args.files:
        f = Path(f)
        out_dir = args.out_dir or f.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f.with_suffix('.blend').name
        print(f'Converting {f} -> {out_file}')

        script = Path(__file__).parent / 'synty_character_fixer.py'
        extra_blender_args = []
        passthrough_args = [str(f), str(out_file)]
        if args.overwrite:
            passthrough_args.append('--overwrite')
        cmd = ['blender', '--background', '--python', script, *extra_blender_args, '--', *passthrough_args]
        try:
            subprocess.run(cmd, check=True, stdout=None if args.verbose else subprocess.DEVNULL)
        except FileNotFoundError as e:
            print('ERROR: Failed to find blender executable. Make sure Blender install is on your PATH.')
            if platform.system() == 'Windows':
                print(r'  For example: setx PATH=%PATH%;C:\Program Files\Blender Foundation\Blender X.XX')
            print()
            raise


if __name__ == '__main__':
    main()
