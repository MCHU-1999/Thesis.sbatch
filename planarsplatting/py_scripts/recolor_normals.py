#!/usr/bin/env python3

import os
import sys
import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt


def plot_normal_map(normal_rgb, title="Normal Map"):
    """Plot normal map for visualization"""
    # normal_array shape: (h, w, 3)
    # Clip values to [0, 1] range for display
    normal_rgb = np.clip(normal_rgb, 0, 1)
    
    plt.figure(figsize=(12, 6))
    
    # Plot the RGB normal map
    plt.subplot(2, 2, 1)
    plt.imshow(normal_rgb)
    plt.title(f"{title} - RGB")
    plt.axis('off')
    
    # Plot individual channels
    plt.subplot(2, 2, 2)
    plt.imshow(normal_rgb[:, :, 0], cmap='Reds')
    plt.title("X Component (Red)")
    plt.axis('off')
    
    plt.subplot(2, 2, 3)
    plt.imshow(normal_rgb[:, :, 1], cmap='Greens')
    plt.title("Y Component (Green)")
    plt.axis('off')
    
    plt.subplot(2, 2, 4)
    plt.imshow(normal_rgb[:, :, 2], cmap='Blues')
    plt.title("Z Component (Blue)")
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def main():
    if len(sys.argv) != 2:
        print("Usage: python recolor_normals.py <input_folder>")
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
            normal_data = np.load(npy_file)
            # normal_data = np.transpose(normal_data, [1,2,0])
            assert normal_data.ndim == 3, f"Expected 3D array, got ndim={normal_data.ndim}"

            print(f"{normal_data.shape=}")
            print(f"{normal_data.max()=}")
            print(f"{normal_data.min()=}")
            print(normal_data[:,:,0])

            # plot_normal_map(normal_data)
            # Normalize normals from [-1, 1] to [0, 255] for RGB visualization
            # Each channel (x, y, z) becomes (R, G, B)
            normal_colored = ((normal_data + 1.0) * 127.5).astype(np.uint8)
            # normal_colored = (normal_data * 255).astype(np.uint8)
            # OpenCV expects BGR format, so convert RGB to BGR
            normal_colored = cv2.cvtColor(normal_colored, cv2.COLOR_RGB2BGR)
            # Save as PNG in same folder
            output_file = npy_file.with_suffix('.png')
            cv2.imwrite(str(output_file), normal_colored)
            
            print(f"✓ {npy_file.name} -> {output_file.name}")
            
        except Exception as e:
            print(f"✗ Error with {npy_file.name}: {e}")
    
    print("Done!")

if __name__ == "__main__":
    main()