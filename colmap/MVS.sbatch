#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=short
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:a40:1     # Request 1 GPU per task
#SBATCH --mem=32GB
#SBATCH --output=slurm_mvs_%j.out
#SBATCH --error=slurm_mvs_%j.err

# --- Configuration ---
# Point this to the folder containing 'images', 'sparse', and 'stereo'
DATA_PATH=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu/TNT_GOF/TrainingSet/Barn
SIF_PATH=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu/containers/colmap.sif 

echo "--- Starting Job ---"

# --- Environment Setup ---
echo "Loading modules..."
module purge
module use /opt/insy/modulefiles
module load cuda/12.4
module load devtoolset/11
# module load miniconda/3.11

# 2. Run Stereo (MVS)
# This uses the existing 'stereo' folder you already have.
echo "Running Patch Match Stereo..."
srun apptainer exec --nv \
    -B /tudelft.net/:/tudelft.net/ \
    $SIF_PATH \
    colmap patch_match_stereo \
        --workspace_path $DATA_PATH \
        --workspace_format COLMAP \
        --PatchMatchStereo.geom_consistency true

# 3. Run Fusion
echo "Running Stereo Fusion..."
srun apptainer exec --nv \
    -B /tudelft.net/:/tudelft.net/ \
    $SIF_PATH \
    colmap stereo_fusion \
        --workspace_path $DATA_PATH \
        --workspace_format COLMAP \
        --input_type geometric \
        --output_path $DATA_PATH/colmap_mvs_fused.ply

echo "--- Finished ---"