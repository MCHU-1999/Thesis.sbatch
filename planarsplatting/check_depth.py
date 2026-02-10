import numpy as np
import matplotlib.pyplot as plt



NPY_FILE = "/Users/mchu/Documents/TUD/Thesis/PlanarSplatting/planarSplat_ExpRes/exp_tnt_prior/plane2000_s6_i20000_Barn/maskoff/scaled_depth/000001.npy"

if __name__ == "__main__":
    depth_data = np.load(NPY_FILE)
    print(f"Shape: {depth_data.shape}")
    print(f"Min: {depth_data.min():.4f}, Max: {depth_data.max():.4f}")
    print(f"Mean: {depth_data.mean():.4f}, Std: {depth_data.std():.4f}")
    print(depth_data)
    
    # Handle 3D arrays
    if depth_data.ndim == 3:
        depth_data = depth_data[:, :, 0]
        print("Using first channel of 3D array")
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.imshow(depth_data, cmap='viridis')
    plt.title('Depth Map (Viridis)')
    plt.colorbar()
    
    plt.subplot(2, 2, 2)
    plt.imshow(depth_data, cmap='jet')
    plt.title('Depth Map (Jet)')
    plt.colorbar()
    
    plt.subplot(2, 2, 3)
    plt.hist(depth_data.flatten(), bins=50, alpha=0.7)
    plt.title('Depth Value Distribution')
    plt.xlabel('Depth Value')
    plt.ylabel('Frequency')
    
    plt.subplot(2, 2, 4)
    plt.imshow(depth_data, cmap='gray')
    plt.title('Depth Map (Grayscale)')
    plt.colorbar()
    
    plt.tight_layout()
    plt.show()