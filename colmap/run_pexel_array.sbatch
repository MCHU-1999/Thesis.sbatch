#!/bin/sh

#SBATCH --partition=general
#SBATCH --time=12:00:00      # 12 hours to safely cover both SfM and MVS
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16   # 16 CPU threads for heavy CPU steps (Mapper, Fusion)
#SBATCH --mem=32GB
#SBATCH --gres=gpu:a40:1

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
mkdir -p ${DATA_PATH}/sparse
mkdir -p ${DATA_PATH}/dense

# ==========================================
# PHASE 1: SPARSE RECONSTRUCTION (SfM)
# ==========================================
echo "[1/6] Feature Extraction..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap feature_extractor \
        --database_path ${DATA_PATH}/database.db \
        --image_path ${DATA_PATH}/images

echo "[2/6] Feature Matching..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap sequential_matcher \
        --database_path ${DATA_PATH}/database.db

echo "[3/6] Sparse Mapping..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap mapper \
        --database_path ${DATA_PATH}/database.db \
        --image_path ${DATA_PATH}/images \
        --output_path ${DATA_PATH}/sparse

# ==========================================
# PHASE 2: DENSE RECONSTRUCTION (MVS)
# ==========================================
echo "[4/6] Image Undistortion..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap image_undistorter \
        --image_path ${DATA_PATH}/images \
        --input_path ${DATA_PATH}/sparse/0 \
        --output_path ${DATA_PATH}/dense \
        --output_type COLMAP

echo "[5/6] Patch Match Stereo..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap patch_match_stereo \
        --workspace_path ${DATA_PATH}/dense \
        --workspace_format COLMAP \
        --PatchMatchStereo.geom_consistency true \
        --PatchMatchStereo.max_image_size 1024

echo "[6/6] Stereo Fusion..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap stereo_fusion \
        --workspace_path ${DATA_PATH}/dense \
        --workspace_format COLMAP \
        --input_type geometric \
        --output_path ${DATA_PATH}/dense/fused.ply

echo "--- COLMAP Pipeline finished for: ${CURRENT_DATASET} ---"