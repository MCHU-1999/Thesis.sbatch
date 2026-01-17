#!/usr/bin/env python3
"""
Script to analyze depth maps stored in .npy files
Reads all .npy files in a directory and prints min/max depth values
"""

import os
import sys
import numpy as np
from pathlib import Path
import argparse


def analyze_depth_file(filepath):
    """
    Analyze a single .npy depth file
    
    Args:
        filepath (str): Path to the .npy file
        
    Returns:
        tuple: (filename, min_depth, max_depth, mean_depth, shape)
    """
    try:
        # Load the depth map
        depth_map = np.load(filepath)
        
        # Handle different data types and potential invalid values
        if depth_map.dtype == np.float32 or depth_map.dtype == np.float64:
            # Remove NaN and infinite values for statistics
            valid_depths = depth_map[np.isfinite(depth_map)]
            if len(valid_depths) == 0:
                return (os.path.basename(filepath), None, None, None, depth_map.shape)
        else:
            valid_depths = depth_map[depth_map > 0]  # Assume 0 is invalid for integer depths
        
        min_depth = np.min(valid_depths) if len(valid_depths) > 0 else None
        max_depth = np.max(valid_depths) if len(valid_depths) > 0 else None
        mean_depth = np.mean(valid_depths) if len(valid_depths) > 0 else None
        
        return (os.path.basename(filepath), min_depth, max_depth, mean_depth, depth_map.shape)
        
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return (os.path.basename(filepath), None, None, None, None)


def analyze_depth_directory(directory_path, pattern="*.npy", verbose=False):
    """
    Analyze all depth files in a directory
    
    Args:
        directory_path (str): Path to directory containing .npy files
        pattern (str): File pattern to match (default: "*.npy")
        verbose (bool): Print detailed info for each file
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Error: Directory '{directory_path}' does not exist!")
        return
    
    # Find all .npy files
    npy_files = sorted(list(directory.glob(pattern)))
    
    if not npy_files:
        print(f"No .npy files found in '{directory_path}'")
        return
    
    print(f"Found {len(npy_files)} .npy files in '{directory_path}'")
    print("=" * 80)
    
    # Statistics tracking
    all_min_depths = []
    all_max_depths = []
    all_mean_depths = []
    valid_files = 0
    
    # Process each file
    for i, filepath in enumerate(npy_files, 1):
        filename, min_depth, max_depth, mean_depth, shape = analyze_depth_file(filepath)
        
        if min_depth is not None:
            all_min_depths.append(min_depth)
            all_max_depths.append(max_depth)
            all_mean_depths.append(mean_depth)
            valid_files += 1
        
        if verbose:
            if min_depth is not None:
                print(f"{i:3d}. {filename}")
                print(f"     Shape: {shape}")
                print(f"     Min depth: {min_depth:.4f}")
                print(f"     Max depth: {max_depth:.4f}")
                print(f"     Mean depth: {mean_depth:.4f}")
            else:
                print(f"{i:3d}. {filename} - ERROR or no valid depths")
            print()
        else:
            # Compact output
            if min_depth is not None:
                print(f"{i:3d}. {filename:<30} | Min: {min_depth:8.4f} | Max: {max_depth:8.4f} | Mean: {mean_depth:8.4f} | Shape: {shape}")
            else:
                print(f"{i:3d}. {filename:<30} | ERROR or no valid depths")
    
    # Summary statistics
    print("=" * 80)
    print(f"SUMMARY ({valid_files}/{len(npy_files)} valid files):")
    
    if all_min_depths:
        global_min = min(all_min_depths)
        global_max = max(all_max_depths)
        overall_mean = np.mean(all_mean_depths)
        
        print(f"Global minimum depth: {global_min:.6f}")
        print(f"Global maximum depth: {global_max:.6f}")
        print(f"Average mean depth: {overall_mean:.6f}")
        print(f"Depth range: {global_max - global_min:.6f}")
    else:
        print("No valid depth data found in any files!")


def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Analyze depth maps stored in .npy files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python depth_analysis.py /path/to/depth/maps
  python depth_analysis.py /path/to/depth/maps --verbose
  python depth_analysis.py /path/to/depth/maps --pattern "depth_*.npy"
        """
    )
    
    parser.add_argument(
        "directory",
        help="Directory containing .npy depth files"
    )
    parser.add_argument(
        "--pattern", "-p",
        default="*.npy",
        help="File pattern to match (default: *.npy)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed information for each file"
    )
    
    args = parser.parse_args()
    
    # Analyze the directory
    analyze_depth_directory(args.directory, args.pattern, args.verbose)


if __name__ == "__main__":
    main()