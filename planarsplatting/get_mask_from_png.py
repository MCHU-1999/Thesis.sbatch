import argparse
from pathlib import Path
from PIL import Image

def process_images(input_dir, output_dir, threshold=0):
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    input_path = Path(input_dir)
    if not input_path.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")
    
    # Supported extensions
    extensions = {".png", ".PNG"}

    for file_path in input_path.iterdir():
        if file_path.suffix in extensions:
            try:
                with Image.open(file_path) as img:
                    # If the image has an alpha channel (RGBA or LA)
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        # Normalize to RGBA so alpha is always available as the 4th channel.
                        alpha = img.convert("RGBA").getchannel("A")
                        # Binary mask: black (0) = masked, white (255) = kept.
                        new_img = alpha.point(lambda a: 255 if a > threshold else 0, mode="L")
                    else:
                        print(f"Skipping {file_path.name}: no alpha channel")
                        continue

                    # Save as PNG mask.
                    output_file = output_path / f"{file_path.stem}.png"
                    new_img.save(output_file, "PNG")
                    print(f"Mask written: {file_path.name} -> {output_file.name}")
            
            except Exception as e:
                print(f"Failed to process {file_path.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract alpha channel from PNG files as binary masks (black=masked, white=kept)."
    )
    parser.add_argument("input_dir", help="Directory containing PNG files")
    parser.add_argument("output_dir", help="Directory to save binary mask PNG files")
    parser.add_argument(
        "--threshold",
        type=int,
        default=0,
        help="Alpha threshold (0-255). Pixels with alpha > threshold become white; otherwise black. Default: 0",
    )
    
    args = parser.parse_args()
    if not (0 <= args.threshold <= 255):
        raise ValueError("--threshold must be between 0 and 255")

    process_images(args.input_dir, args.output_dir, threshold=args.threshold)