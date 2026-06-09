#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=short          # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=4:00:00       # Request run time (wall-clock) per job.
#SBATCH --ntasks=1           # Request number of parallel tasks per job.
#SBATCH --cpus-per-task=16   # Request number of CPUs (threads) per task.
#SBATCH --mem=32GB           # Request memory per node.
#SBATCH --mail-type=END      # Set mail type to 'END' to receive a mail when the job finishes.
#SBATCH --gres=gpu:a40:1     # Request 1 GPU per task

# --- ARRAY CONFIGURATION ---
# 0-8 creates exactly 9 jobs. 
# %A is the master array job ID, %a is the specific task ID (0 to 8).
#SBATCH --array=0-8
#SBATCH --output=slurm_colmap_%A_%a.out
#SBATCH --error=slurm_colmap_%A_%a.err

# --- Environment Setup ---
module purge
module use /opt/insy/modulefiles

# --- Define Your 9 Folders Here ---
# Add the exact names of your 9 folders inside the parentheses, separated by spaces or newlines.
DATASETS=(
    "church-cadeby"
    "church-chesterfield"
    "killingbeck-cemetery"
    "moskee-haarlem"
    "tower-court"
    "wotrubakirche"
    "elbphilharmonie"
    "krasna-horka-castle"
    "clocktower"
)

# Fetch the dataset for this specific array task
CURRENT_DATASET=${DATASETS[$SLURM_ARRAY_TASK_ID]}

# --- Paths ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
DATA_PATH=${MY_STORAGE}/Pexels/${CURRENT_DATASET}
SIF_PATH=${MY_STORAGE}/containers/colmap.sif 

echo "--- Starting COLMAP Pipeline for: ${CURRENT_DATASET} ---"
echo "Array Job ID: ${SLURM_ARRAY_JOB_ID} | Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Data Path: ${DATA_PATH}"

# Ensure base directories exist
mkdir -p ${DATA_PATH}/dense

# ==========================================
# PHASE 2: DENSE RECONSTRUCTION (MVS)
# ==========================================
echo "[1/3] Image Undistortion..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap image_undistorter \
        --image_path ${DATA_PATH}/images \
        --input_path ${DATA_PATH}/DA3_colmap \
        --output_path ${DATA_PATH}/dense \
        --output_type COLMAP

echo "[2/3] Patch Match Stereo..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap patch_match_stereo \
        --workspace_path ${DATA_PATH}/dense \
        --workspace_format COLMAP \
        --PatchMatchStereo.geom_consistency true \
        --PatchMatchStereo.max_image_size 1024

echo "[3/3] Stereo Fusion..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap stereo_fusion \
        --workspace_path ${DATA_PATH}/dense \
        --workspace_format COLMAP \
        --input_type geometric \
        --output_path ${DATA_PATH}/dense/fused.ply

echo "--- COLMAP Pipeline finished for: ${CURRENT_DATASET} ---"