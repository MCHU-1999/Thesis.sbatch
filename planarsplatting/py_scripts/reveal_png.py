import os
import argparse
from pathlib import Path
from PIL import Image

def process_images(input_dir, output_dir):
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    input_path = Path(input_dir)
    
    # Supported extensions
    extensions = {".png", ".PNG"}

    for file_path in input_path.iterdir():
        if file_path.suffix in extensions:
            try:
                with Image.open(file_path) as img:
                    # If the image has an alpha channel (RGBA or LA)
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        # Convert to RGBA to ensure we have 4 channels
                        img = img.convert("RGBA")
                        
                        # Split the channels
                        r, g, b, a = img.split()
                        
                        # Create a new RGB image using only the color channels
                        # This ignores the 'a' (alpha) mask entirely, 
                        # revealing the raw RGB data underneath.
                        new_img = Image.merge("RGB", (r, g, b))
                    else:
                        # If no alpha channel, just convert to RGB
                        new_img = img.convert("RGB")

                    # Save as JPG
                    output_file = output_path / f"{file_path.stem}.jpg"
                    new_img.save(output_file, "JPEG", quality=95)
                    print(f"Converted: {file_path.name} -> {output_file.name}")
            
            except Exception as e:
                print(f"Failed to process {file_path.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PNG to JPG and reveal hidden transparent data.")
    parser.add_argument("input_dir", help="Directory containing PNG files")
    parser.add_argument("output_dir", help="Directory to save JPG files")
    
    args = parser.parse_args()
    process_images(args.input_dir, args.output_dir)