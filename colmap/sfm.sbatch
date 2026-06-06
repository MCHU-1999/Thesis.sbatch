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
#SBATCH --output=slurm_sfm_%j.out
#SBATCH --error=slurm_sfm_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
DATA_PATH=${MY_STORAGE}/synthetic/WoodenHouse
SIF_PATH=${MY_STORAGE}/containers/colmap.sif 

echo "--- Starting COLMAP Processing Job ---"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Data Path: ${DATA_PATH}"
echo "Container: ${SIF_PATH}"

# --- Environment Setup ---
echo "Loading modules..."
module purge
module use /opt/insy/modulefiles
module load apptainer

# --- Execution Command ---
echo "Running COLMAP SfM..."

# 1. Feature Extraction (uses GPU)
apptainer exec --nv ${SIF_PATH} colmap feature_extractor \
    --database_path ${DATA_PATH}/database.db \
    --image_path ${DATA_PATH}/images

# 2. Feature Matching (uses GPU)
apptainer exec --nv ${SIF_PATH} colmap exhaustive_matcher \
    --database_path ${DATA_PATH}/database.db

# 3. Sparse Mapping (CPU intensive)
mkdir -p ${DATA_PATH}/sparse
apptainer exec --nv ${SIF_PATH} colmap mapper \
    --database_path ${DATA_PATH}/database.db \
    --image_path ${DATA_PATH}/images \
    --output_path ${DATA_PATH}/sparse

echo "--- COLMAP SfM job finished ---"