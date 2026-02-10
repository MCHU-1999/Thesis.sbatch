#!/usr/bin/env python3

import os
import sys
import numpy as np
import cv2
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python recolor_maps.py <input_folder>")
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
            
            # Handle 3D arrays by taking first channel
            if depth_data.ndim == 3:
                depth_data = depth_data[:, :, 0]
            
            # Normalize depth map
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