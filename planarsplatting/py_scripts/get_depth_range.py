import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
from PIL import Image

# IMAGE_FOLDER = "/Users/mchu/Documents/TUD/Thesis/DTU/scan24/images"
# DEPTH_FOLDER = "/Users/mchu/Documents/TUD/Thesis/DTU/scan24/DA3_depth"
# MASK_FOLDER = "/Users/mchu/Documents/TUD/Thesis/DTU/scan24/fg_masks"
# IMAGE_FOLDER = "/Users/mchu/Documents/TUD/Thesis/TNT_GOF/TrainingSet/Barn/images"
# DEPTH_FOLDER = "/Users/mchu/Documents/TUD/Thesis/TNT_GOF/TrainingSet/Barn/DA3_depth"
# MASK_FOLDER = "/Users/mchu/Documents/TUD/Thesis/TNT_GOF/TrainingSet/Barn/fg_masks"
IMAGE_FOLDER = "/Users/mchu/Documents/TUD/Thesis/Pexels/moskee-haarlem/images"
DEPTH_FOLDER = "/Users/mchu/Documents/TUD/Thesis/Pexels/moskee-haarlem/DA3_depth"
MASK_FOLDER = "/Users/mchu/Documents/TUD/Thesis/Pexels/moskee-haarlem/fg_masks"

def _resolve_by_stem(folder: str, stem: str, extensions):
    for ext in extensions:
        candidate = os.path.join(folder, f"{stem}{ext}")
        if os.path.exists(candidate):
            return candidate
    return None


def process_one(image_folder: str, depth_folder: str, mask_folder: str, depth_filename: str):
    depth_path = os.path.join(depth_folder, depth_filename)
    stem = Path(depth_filename).stem

    image_path = _resolve_by_stem(image_folder, stem, [".png", ".jpg", ".jpeg", ".JPG", ".PNG"])
    mask_path = _resolve_by_stem(mask_folder, stem, [".png", ".jpg", ".jpeg", ".JPG", ".PNG"])

    if image_path is None:
        print(f"Image not found for stem: {stem}")
        return
    if not os.path.exists(depth_path):
        print(f"Depth file not found: {depth_path}")
        return
    if mask_path is None:
        print(f"Mask not found for stem: {stem}")
        return
    
    try:
        # Load images
        depth = np.load(depth_path)
        if depth.ndim == 3:
            depth = np.squeeze(depth)

        image = np.array(Image.open(image_path).convert("RGB"))
        fg_mask = np.array(Image.open(mask_path).convert("L")) > 0

        valid_depth = depth[(depth > 0) & fg_mask]
        if valid_depth.size == 0:
            print(f"No valid depth values for {stem}")
            return

        p95 = np.percentile(valid_depth, 95)
        p100 = np.max(valid_depth)

        # 1) Build binary mask: keep pixels with 0 < depth < max, inside fg mask.
        new_binary_mask = (((depth > 0) & (depth < p95)) | (fg_mask)).astype(np.uint8)

        # 2) Use mask to clip image.
        clipped_image = image * new_binary_mask[..., None]

        # Plotting
        plt.figure(figsize=(22, 4))

        plt.subplot(1, 5, 1)
        plt.imshow(image)
        plt.title("Original Image")
        plt.axis("off")

        plt.subplot(1, 5, 2)
        plt.imshow(fg_mask, cmap="gray")
        plt.title("Original FG Mask")
        plt.axis("off")

        plt.subplot(1, 5, 3)
        depth_vis = np.where(depth > 0, depth, np.nan)
        plt.imshow(depth_vis, cmap="jet")
        plt.title("Depth")
        plt.axis("off")

        plt.subplot(1, 5, 4)
        plt.imshow(new_binary_mask, cmap="gray")
        plt.title("new_binary_mask")
        plt.axis("off")

        plt.subplot(1, 5, 5)
        plt.imshow(clipped_image)
        plt.title("Clipped Image")
        plt.axis("off")

        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error processing {depth_filename}: {e}")



if __name__ == "__main__":

    # Find all .npy files
    npy_files = list(Path(DEPTH_FOLDER).glob("*.npy"))
    print(f"Processing {len(npy_files)} files...")
    
    for npy_file in npy_files:
        process_one(IMAGE_FOLDER, DEPTH_FOLDER, MASK_FOLDER, npy_file.name)
            
    print("Done!")