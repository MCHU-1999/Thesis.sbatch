#!/usr/bin/env python3

import os
import sys
import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap, BoundaryNorm

def plot_threshold_depth_map(
    depth_map,
    threshold,
    title="Thresholded Depth Map",
    colors=("royalblue", "tomato"),  # (below, above)
    show=True,
):
    """
    Plot a depth map using exactly 2 colors:
    - colors[0] for values < threshold
    - colors[1] for values >= threshold

    Returns (fig, ax, im).
    """
    depth = np.asarray(depth_map)

    if depth.ndim != 2:
        raise ValueError(f"Expected 2D depth map, got shape {depth.shape}")

    finite = np.isfinite(depth)
    if not np.any(finite):
        raise ValueError("Depth map has no finite values to plot.")

    # Build binary map: 0 -> below threshold, 1 -> above/equal threshold
    binary = np.zeros_like(depth, dtype=np.uint8)
    binary[depth >= threshold] = 1

    # Mask non-finite values so they are not shown
    binary_masked = np.ma.array(binary, mask=~finite)

    cmap = ListedColormap([colors[0], colors[1]])
    norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(binary_masked, cmap=cmap, norm=norm)
    ax.set_title(f"{title} (threshold={threshold})")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1], fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels([f"< {threshold}", f">= {threshold}"])
    cbar.set_label("Depth class", rotation=90)

    plt.tight_layout()
    if show:
        plt.show()

    return fig, ax, im

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

    if depth.ndim != 2:
        raise ValueError(f"Expected 2D depth map, got shape {depth.shape}")

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

            # plot_threshold_depth_map(depth_data, 4.0, npy_file.name)
            plot_depth_map(depth_data, npy_file.name)
            
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