#!/usr/bin/env python3

import os
import sys
import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt

def plot_depth_map(
    depth_map,
    title="Depth Map",
    cmap="jet",
    show=True,
):
    """
    Plot a single depth map with a side colorbar legend.
    Returns (fig, ax, im) so you can reuse or save externally.
    """
    depth = np.asarray(depth_map)

    # If input is HxWxC, take first channel
    if depth.ndim == 3:
        depth = depth[:, :, 0]

    if depth.ndim != 2:
        raise ValueError(f"Expected 2D depth map (or 3D with channels), got shape {depth.shape}")

    # Robust min/max from finite values only
    finite = np.isfinite(depth)
    if not np.any(finite):
        raise ValueError("Depth map has no finite values to plot.")

    vmin = np.min(depth[finite])
    vmax = np.max(depth[finite])

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(depth, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # Side legend for depth values
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Depth value", rotation=90)

    plt.tight_layout()
    if show:
        plt.show()

    return fig, ax, im

def main():
    if len(sys.argv) != 2:
        print("Usage: python recolor_depths.py <input_folder>")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    input_path = Path(input_folder)
    
    if not input_path.exists():
        print(f"Error: Folder {input_folder} does not exist")
        sys.exit(1)
    
    # Find all .npy files
    npy_files = list(input_path.glob("*.npy"))
    
    if not npy_files:
        print("No .npy files found")
        return
    
    print(f"Processing {len(npy_files)} files...")
    
    for npy_file in npy_files:
        try:
            # Load depth data
            depth_data = np.load(npy_file)

            plot_depth_map(depth_data, npy_file.name)
            
            # Handle 3D arrays by taking first channel
            if depth_data.ndim == 3:
                depth_data = depth_data[:, :, 0]
            
            # Normalize depth map
            # depth_data = np.clip(depth_data, 0, 100)
            depth_normalized = (depth_data - depth_data.min()) / (depth_data.max() - depth_data.min() + 1e-8)
            depth_colored = cv2.applyColorMap((depth_normalized * 255).astype(np.uint8), cv2.COLORMAP_JET)
            
            # Save as PNG in same folder
            output_file = npy_file.with_suffix('.png')
            cv2.imwrite(str(output_file), depth_colored)
            
            print(f"✓ {npy_file.name} -> {output_file.name}")
            
        except Exception as e:
            print(f"✗ Error with {npy_file.name}: {e}")
    
    print("Done!")

if __name__ == "__main__":
    main()