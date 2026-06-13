import sys
import numpy as np
from scipy.spatial.transform import Rotation

def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_centers.py <input_images.txt> <output_reference.txt>")
        sys.exit(1)

    input_txt = sys.argv[1]
    output_txt = sys.argv[2]

    with open(input_txt, 'r') as f:
        lines = f.readlines()

    with open(output_txt, 'w') as out:
        for line in lines:
            if line.startswith('#'):
                continue
            
            parts = line.strip().split()
            
            # An image pose line has at least 10 elements and ends with the filename
            if len(parts) >= 10 and parts[9].lower().endswith(('.jpg', '.png', '.jpeg')):
                try:
                    # COLMAP quaternions are scalar-first (qw, qx, qy, qz)
                    qw, qx, qy, qz = map(float, parts[1:5])
                    
                    # Translation vector (tx, ty, tz)
                    t_vec = np.array(list(map(float, parts[5:8])))
                    
                    image_name = parts[9]
                    
                    # Scipy requires scalar-last format (qx, qy, qz, qw)
                    rot = Rotation.from_quat([qx, qy, qz, qw])
                    rot_matrix = rot.as_matrix()
                    
                    # Calculate camera center: C = -(R^T) * T
                    camera_center = -np.dot(rot_matrix.T, t_vec)
                    
                    # Write to the reference file
                    out.write(f"{image_name} {camera_center[0]:.6f} {camera_center[1]:.6f} {camera_center[2]:.6f}\n")
                except ValueError:
                    pass

    print(f"Successfully wrote camera centers to {output_txt}")

if __name__ == "__main__":
    main()