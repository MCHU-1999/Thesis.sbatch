import argparse
import os
from PIL import Image
import numpy as np

def check_dimensions(image_folder, depth_folder, normal_folder):
    """
    Checks if images, depth maps, and normal maps have the same height and width.

    Args:
        image_folder (str): Path to the folder containing images.
        depth_folder (str): Path to the folder containing depth maps (.npy).
        normal_folder (str): Path to the folder containing normal maps (.npy).
    """
    image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

    for image_file in image_files:
        base_filename, _ = os.path.splitext(image_file)
        
        image_path = os.path.join(image_folder, image_file)
        depth_path = os.path.join(depth_folder, base_filename + '.npy')
        normal_path = os.path.join(normal_folder, base_filename + '.npy')

        # Check if corresponding depth and normal files exist
        if not os.path.exists(depth_path):
            print(f"Warning: Depth file not found for {image_file}: {depth_path}")
            continue
        if not os.path.exists(normal_path):
            print(f"Warning: Normal file not found for {image_file}: {normal_path}")
            continue

        try:
            # Read image and get dimensions
            with Image.open(image_path) as img:
                img_width, img_height = img.size

            # Read depth map and get dimensions
            depth_map = np.load(depth_path)
            depth_height, depth_width = depth_map.shape

            # Read normal map and get dimensions
            normal_map = np.load(normal_path)
            if normal_map.shape[0] != 3:
                print(f"Warning: Normal map for {image_file} does not have 3 channels: {normal_map.shape}")
                continue
            _, normal_height, normal_width = normal_map.shape

            # Check for consistent dimensions
            if not (img_height == depth_height == normal_height and img_width == depth_width == normal_width):
                print(f"Dimension mismatch for {base_filename}:")
                print(f"  Image:  (H: {img_height}, W: {img_width})")
                print(f"  Depth:  (H: {depth_height}, W: {depth_width})")
                print(f"  Normal: (H: {normal_height}, W: {normal_width})")
            else:
                print(f"Dimensions for {base_filename} are consistent.")

        except Exception as e:
            print(f"Error processing {image_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check dimensions of images, depth maps, and normal maps.")
    parser.add_argument("image_folder", type=str, help="Path to the folder containing images.")
    parser.add_argument("depth_folder", type=str, help="Path to the folder containing depth maps (.npy).")
    parser.add_argument("normal_folder", type=str, help="Path to the folder containing normal maps (.npy).")

    args = parser.parse_args()

    check_dimensions(args.image_folder, args.depth_folder, args.normal_folder)


    # How to run:
    # python dim_check.py ~/mount/Deep3D/mingchiehhu/TNT_GOF/TrainingSet/Barn/images ~/mount/Deep3D/mingchiehhu/PGSR/output_tnt/Barn/test/train/ours_30000/renders_depth ~/mount/Deep3D/mingchiehhu/PGSR/output_tnt/Barn/test/train/ours_30000/renders_normal