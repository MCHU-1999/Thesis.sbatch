#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=short          # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=4:00:00       # Request run time (wall-clock) per job.
#SBATCH --ntasks=1           # Request number of parallel tasks per job.
#SBATCH --cpus-per-task=8    # Request number of CPUs (threads) per task.
#SBATCH --mem=32GB           # Request memory per node.
#SBATCH --mail-type=END      # Set mail type to 'END' to receive a mail when the job finishes.
#SBATCH --gres=gpu:a40:1     # Request 1 GPU per task

# Set output/error logs
#SBATCH --output=slurm_mvs_%j.out
#SBATCH --error=slurm_mvs_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
DATA_PATH=${MY_STORAGE}/colmap_test/Barn
SIF_PATH=${MY_STORAGE}/containers/colmap.sif 

echo "--- Starting COLMAP MVS Job ---"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Data Path: ${DATA_PATH}"
echo "Container: ${SIF_PATH}"

# --- Environment Setup ---
echo "Loading modules..."
module purge
module use /opt/insy/modulefiles

# --- Execution Command ---
echo "Running COLMAP MVS..."

# 1. Image Undistortion (Reads from sparse/0)
mkdir -p ${DATA_PATH}/dense
srun apptainer exec \
    --nv \
    -B /tudelft.net/:/tudelft.net/ \
    --pwd ${DATA_PATH} \
    ${SIF_PATH} \
    colmap image_undistorter \
        --image_path ${DATA_PATH}/images \
        --input_path ${DATA_PATH}/sparse/0 \
        --output_path ${DATA_PATH}/dense \
        --output_type COLMAP

# 2. Patch Match Stereo (Heavy GPU usage)
srun apptainer exec \
    --nv \
    -B /tudelft.net/:/tudelft.net/ \
    --pwd ${DATA_PATH} \
    ${SIF_PATH} \
    colmap patch_match_stereo \
        --workspace_path ${DATA_PATH}/dense \
        --workspace_format COLMAP \
        --PatchMatchStereo.geom_consistency true

# 3. Stereo Fusion (Fuses depth maps to point cloud)
srun apptainer exec \
    --nv \
    -B /tudelft.net/:/tudelft.net/ \
    --pwd ${DATA_PATH} \
    ${SIF_PATH} \
    colmap stereo_fusion \
        --workspace_path ${DATA_PATH}/dense \
        --workspace_format COLMAP \
        --input_type geometric \
        --output_path ${DATA_PATH}/dense/fused.ply

echo "--- COLMAP MVS job finished ---"