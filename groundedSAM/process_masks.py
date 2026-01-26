import os
import cv2
import numpy as np
import supervision as sv
from tqdm import tqdm
from autodistill_grounded_sam import GroundedSAM
from autodistill.detection import CaptionOntology

# --- CONFIGURATION ---
# Replace these with your actual HPC paths
MY_STORAGE = "/tudelft.net/staff-umbrella/Deep3D/mingchiehhu"
IMAGE_DIR = f"{MY_STORAGE}/TNT_GOF/TrainingSet/Barn/images"
OUTPUT_DIR = f"{MY_STORAGE}/TNT_GOF/TrainingSet/Barn/masked_images"
# Define the object and its label
# Format: {"text prompt to find": "label name"}
ONTOLOGY = CaptionOntology({"the person": "person"})

def main():
    # 1. Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    # 2. Initialize Grounded-SAM
    # It will look for weights in ~/.cache/autodistill unless redirected
    print("Loading Grounded-SAM...")
    base_model = GroundedSAM(ontology=ONTOLOGY)

    # 3. List images
    extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(extensions)]
    print(f"Found {len(image_files)} images. Starting inference...")

    # 4. Process loop
    for filename in tqdm(image_files):
        img_path = os.path.join(IMAGE_DIR, filename)
        
        try:
            # Inference
            results = base_model.predict(img_path)

            if results.mask is not None and len(results.mask) > 0:
                # results.mask is usually a boolean array [N, H, W]
                # We take the first mask found and convert to 0-255 uint8
                combined_mask = np.any(results.mask, axis=0).astype(np.uint8) * 255
                
                # Save mask with the same filename
                save_path = os.path.join(OUTPUT_DIR, f"mask_{os.path.splitext(filename)[0]}.png")
                cv2.imwrite(save_path, combined_mask)
            else:
                print(f"No mask detected for {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"\nProcessing complete. Masks saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()