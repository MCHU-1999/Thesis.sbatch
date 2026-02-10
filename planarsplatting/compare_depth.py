import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path



FOLDER1 = "/Users/mchu/Documents/TUD/Thesis/PlanarSplatting/planarSplat_ExpRes/exp_tnt_prior/plane2000_s6_i20000_Barn/maskon/scaled_depth/"
FOLDER2 = "/Users/mchu/Documents/TUD/Thesis/PlanarSplatting/planarSplat_ExpRes/exp_tnt_prior/plane2000_s6_i20000_Barn/maskon/aligned_depth/"

if __name__ == "__main__":
    path1 = Path(FOLDER1)
    path2 = Path(FOLDER2)
    
    # Get all .npy files from both folders
    npy_files1 = {f.name: f for f in path1.glob("*.npy")}
    npy_files2 = {f.name: f for f in path2.glob("*.npy")}
    
    # Find common files
    common_files = set(npy_files1.keys()) & set(npy_files2.keys())
    
    if not common_files:
        print("No common .npy files found!")
        exit(1)
    
    print(f"Found {len(common_files)} common files")
    print("-" * 50)
    
    total_errors = {}
    all_errors = []
    
    for filename in sorted(common_files):
        try:
            # Load both depth maps
            depth1 = np.load(npy_files1[filename])
            depth2 = np.load(npy_files2[filename])
            
            # Handle 3D arrays
            if depth1.ndim == 3:
                depth1 = depth1[:, :, 0]
            if depth2.ndim == 3:
                depth2 = depth2[:, :, 0]
            
            # Check shapes match
            if depth1.shape != depth2.shape:
                print(f"⚠️  {filename}: Shape mismatch {depth1.shape} vs {depth2.shape}")
                continue
            
            # Calculate different error metrics
            mse = np.mean((depth1 - depth2) ** 2)
            mae = np.mean(np.abs(depth1 - depth2))
            max_error = np.max(np.abs(depth1 - depth2))
            
            total_errors[filename] = {
                'mse': mse,
                'mae': mae, 
                'max_error': max_error
            }
            all_errors.append(mse)
            
            print(f"{filename}:")
            print(f"  MSE: {mse:.6f}")
            print(f"  MAE: {mae:.6f}")
            print(f"  Max Error: {max_error:.6f}")
            print()
            
        except Exception as e:
            print(f"❌ Error with {filename}: {e}")
    
    # Summary statistics
    if all_errors:
        print("=" * 50)
        print("SUMMARY:")
        print(f"Average MSE: {np.mean(all_errors):.6f}")
        print(f"Min MSE: {np.min(all_errors):.6f}")
        print(f"Max MSE: {np.max(all_errors):.6f}")
        print(f"Std MSE: {np.std(all_errors):.6f}")
        
        # Find file with biggest MSE
        max_mse_file = max(total_errors, key=lambda x: total_errors[x]['mse'])
        max_mse_value = total_errors[max_mse_file]['mse']
        print(f"Biggest MSE: {max_mse_file} (MSE: {max_mse_value:.6f})")
        
        # Plot error distribution
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.hist(all_errors, bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('MSE')
        plt.ylabel('Frequency')
        plt.title('MSE Distribution')
        
        plt.subplot(1, 2, 2)
        filenames_sorted = sorted(total_errors.keys())
        mse_values = [total_errors[f]['mse'] for f in filenames_sorted]
        plt.plot(mse_values, 'o-', linewidth=2)
        plt.xlabel('File Index')
        plt.ylabel('MSE')
        plt.title('MSE per File')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
