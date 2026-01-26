#!/bin/sh

#SBATCH --partition=general
#SBATCH --qos=short
#SBATCH --time=4:00:00       # 4 hours is usually plenty for COLMAP
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8    # Increased CPUs for faster matching
#SBATCH --mem=32GB           # 32GB is sufficient for conversion
#SBATCH --mail-type=END

# Set output/error logs
#SBATCH --output=slurm_colmap_%j.out
#SBATCH --error=slurm_colmap_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/runs/colmap

# CHANGE THIS to the folder containing your 'input' subfolder
DATA_PATH=${MY_STORAGE}/TNT_GOF/TrainingSet/Barn_masked

# CHANGE THIS to point to the new container you built
SIF_PATH=${MY_STORAGE}/containers/colmap.sif 

echo "--- Starting COLMAP Processing Job ---"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Data Path: ${DATA_PATH}"
echo "Container: ${SIF_PATH}"

# --- Environment Setup ---
echo "Loading modules..."
module purge
module use /opt/insy/modulefiles

# --- Execution Command ---
echo "Running convert.py..."

# Note:
# 1. We use 'python3' (standard in the colmap container).
# 2. We added '--camera PINHOLE' for your synthetic Rhino data.

srun --chdir=${REPO_PATH} apptainer exec \
    -B $HOME:$HOME \
    -B /tudelft.net/:/tudelft.net/ \
    ${SIF_PATH} \
    python3 convert.py \
        -s "${DATA_PATH}" \
        --camera PINHOLE \
        --no_gpu

echo "--- COLMAP job finished ---"
