"""
Scan a DTU dataset directory and print the contents of every cameras.npz found.

Usage:
    python inspect_npz.py /path/to/your/dtu_dataset
"""

import sys
import numpy as np
from pathlib import Path


def inspect_npz(npz_path: Path):
    data = np.load(npz_path)
    keys = sorted(data.files)

    # Group keys by type (world_mat_N, scale_mat_N, ...)
    prefixes = {}
    for k in keys:
        prefix = '_'.join(k.split('_')[:-1])  # e.g. "world_mat", "scale_mat"
        prefixes.setdefault(prefix, []).append(k)

    print(f"\n{'='*60}")
    print(f"  {npz_path}")
    print(f"{'='*60}")
    print(f"  Total keys : {len(keys)}")
    for prefix, ks in sorted(prefixes.items()):
        sample = data[ks[0]]
        print(f"  {prefix:20s}  x{len(ks):3d}  shape={sample.shape}  dtype={sample.dtype}")

    # Print the first world_mat and scale_mat in full
    for prefix in ['world_mat', 'scale_mat']:
        key = f'{prefix}_0'
        if key in data:
            print(f"\n  [{key}]")
            print(np.array2string(data[key], prefix='    ', separator=', ', precision=6))


def main():
    if len(sys.argv) < 2:
        print("Usage: python inspect_npz.py /path/to/dtu_dataset")
        sys.exit(1)

    root = Path(sys.argv[1])
    npz_files = sorted(root.rglob('*.npz'))

    if not npz_files:
        print(f"No .npz files found under: {root}")
        sys.exit(1)

    print(f"Found {len(npz_files)} .npz file(s) under: {root}")
    for npz in npz_files:
        inspect_npz(npz)


if __name__ == '__main__':
    main()
