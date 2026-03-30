import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path


# FOLDER1 = "/Users/mchu/Documents/TUD/Thesis/DTU/scan40/DA3_depth"
# FOLDER2 = "/Users/mchu/Documents/TUD/Thesis/DTU/scan40/scaled_depth"
# FOLDER2 = "/Users/mchu/Documents/TUD/Thesis/DTU/scan40/mono_depth"
FOLDER1 = "/Users/mchu/Documents/TUD/Thesis/DTU/scan40/mesh_depth"
FOLDER2 = "/Users/mchu/Documents/TUD/Thesis/DTU/scan40/DA3_depth"
FILE_NAME = "0000.npy"

def compare_one(folder1: str, folder2: str, filename: str):
    file1 = os.path.join(folder1, filename)
    file2 = os.path.join(folder2, filename)
    
    # Check if files exist
    if not os.path.exists(file1):
        print(f"File not found: {file1}")
        return
    if not os.path.exists(file2):
        print(f"File not found: {file2}")
        return
    
    try:
        # Load both depth maps
        depth1 = np.load(file1)
        depth2 = np.load(file2)
        # depth1 = np.clip(depth1, 0, 5)
        # depth2 = np.clip(depth2, 0, 5)
        
        print(f"Comparing: {filename}")
        print(f"File 1 shape: {depth1.shape}, File 2 shape: {depth2.shape}")
        
        # Handle 3D arrays
        if depth1.ndim == 3:
            depth1 = depth1[:, :, 0]
            print("Using first channel of 3D array from file 1")
        if depth2.ndim == 3:
            depth2 = depth2[:, :, 0]
            print("Using first channel of 3D array from file 2")
        
        # Check shapes match
        if depth1.shape != depth2.shape:
            print(f"Shape mismatch: {depth1.shape} vs {depth2.shape}")
            return
        
        # Calculate difference and metrics
        difference = depth1 - depth2
        abs_difference = np.abs(difference)
        
        mse = np.mean(difference ** 2)
        mae = np.mean(abs_difference)
        max_error = np.max(abs_difference)

        # Shared color scale for file1 and file2
        finite1 = depth1[np.isfinite(depth1)]
        finite2 = depth2[np.isfinite(depth2)]

        if finite1.size == 0 or finite2.size == 0:
            print("One of the depth maps has no finite values.")
            return

        shared_min = min(finite1.min(), finite2.min())
        shared_max = max(finite1.max(), finite2.max())

        print(f"Shared range (file1+file2): [{shared_min:.3f}, {shared_max:.3f}]")
        print(f"File 1 range: [{depth1.min():.3f}, {depth1.max():.3f}]")
        print(f"File 2 range: [{depth2.min():.3f}, {depth2.max():.3f}]")
        
        # Create comparison plot
        plt.figure(figsize=(10, 6))
        
        # File 1
        plt.subplot(2, 2, 1)
        plt.imshow(depth1, cmap='jet', vmin=shared_min, vmax=shared_max)
        plt.title(f'File 1: {os.path.basename(folder1)}')
        plt.colorbar()

        # File 2
        plt.subplot(2, 2, 2)
        plt.imshow(depth2, cmap='jet', vmin=shared_min, vmax=shared_max)
        plt.title(f'File 2: {os.path.basename(folder2)}')
        plt.colorbar()
        
        # Absolute difference
        plt.subplot(2, 2, 3)
        plt.imshow(abs_difference, cmap='hot')
        plt.title(f'Absolute Difference\nMAE: {mae:.4f}')
        plt.colorbar()
        
        # Raw difference (can be negative)
        plt.subplot(2, 2, 4)
        plt.imshow(difference, cmap='RdBu_r', vmin=-max_error, vmax=max_error)
        plt.title(f'Raw Difference\nMSE: {mse:.4f}')
        plt.colorbar()
        
        plt.suptitle(f'Depth Comparison: {filename}', fontsize=14)
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error comparing {filename}: {e}")




if __name__ == "__main__":

    # Find all .npy files
    npy_files = list(Path(FOLDER1).glob("*.npy"))
    print(f"Processing {len(npy_files)} files...")
    
    for npy_file in npy_files:
        compare_one(FOLDER1, FOLDER2, npy_file.name)
            
    print("Done!")