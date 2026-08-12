#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=short          # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=4:00:00       # Request run time (wall-clock) per job.
#SBATCH --ntasks=1           # Request number of parallel tasks per job.
#SBATCH --cpus-per-task=8   # Request number of CPUs (threads) per task.
#SBATCH --mem=32GB           # Request memory per node.
#SBATCH --mail-type=END      # Set mail type to 'END' to receive a mail when the job finishes.
#SBATCH --gres=gpu:a40:1     # Request 1 GPU per task

# --- ARRAY CONFIGURATION ---
# 0-4 creates 5 jobs. 
# %A is the master array job ID, %a is the specific task ID (0 to 4).
#SBATCH --array=0-4
#SBATCH --output=slurm_colmap_%A_%a.out
#SBATCH --error=slurm_colmap_%A_%a.err

# --- Environment Setup ---
module purge
module use /opt/insy/modulefiles
set -e

# --- Define Your 9 Folders Here ---
# Add the exact names of your 9 folders inside the parentheses, separated by spaces or newlines.
DATASETS=(
    "Barn-sparse25"
    "Barn-sparse50"
    "Barn-sparse100"
    "Barn-sparse200"
    "Barn-sparse400"
)

# Fetch the dataset for this specific array task
CURRENT_DATASET=${DATASETS[$SLURM_ARRAY_TASK_ID]}

# --- Paths ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
DATA_PATH=${MY_STORAGE}/TNT_GOF/TrainingSet/${CURRENT_DATASET}
PY_PATH=${MY_STORAGE}/runs/colmap
SIF_PATH=${MY_STORAGE}/containers/colmap.sif 

echo "--- Starting COLMAP Pipeline for: ${CURRENT_DATASET} ---"
echo "Array Job ID: ${SLURM_ARRAY_JOB_ID} | Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Data Path: ${DATA_PATH}"

# Ensure base directories exist and are clean
rm -rf ${DATA_PATH}/dense
rm -rf ${DATA_PATH}/sparse_triangulated
rm -rf ${DATA_PATH}/sparse_aligned
rm -f ${DATA_PATH}/database.db

# Ensure base directories exist
mkdir -p ${DATA_PATH}/dense
mkdir -p ${DATA_PATH}/sparse_triangulated
mkdir -p ${DATA_PATH}/sparse_aligned

# Ensure the mandatory third file exists, even if empty
touch ${DATA_PATH}/sparse/0/points3D.txt

# ==========================================
# PHASE 1: INITIALIZED SPARSE RECONSTRUCTION
# ==========================================
echo "[1/4] Feature Extraction..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap feature_extractor \
        --database_path ${DATA_PATH}/database.db \
        --image_path ${DATA_PATH}/images

echo "[2/4] Feature Matching..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap exhaustive_matcher \
        --database_path ${DATA_PATH}/database.db

echo "[3/4] Point Triangulation..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap point_triangulator \
        --database_path ${DATA_PATH}/database.db \
        --image_path ${DATA_PATH}/images \
        --input_path ${DATA_PATH}/sparse/0 \
        --output_path ${DATA_PATH}/sparse_triangulated

echo "[4/4] Bundle Adjustment (Locking Known Poses)..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap bundle_adjuster \
        --input_path ${DATA_PATH}/sparse_triangulated \
        --output_path ${DATA_PATH}/sparse_aligned \
        --BundleAdjustment.refine_focal_length 0 \
        --BundleAdjustment.refine_principal_point 0 \
        --BundleAdjustment.refine_extra_params 0 \
        --BundleAdjustment.refine_extrinsics 0

# ==========================================
# PHASE 2: DENSE RECONSTRUCTION (MVS)
# ==========================================
echo "[4/6] Image Undistortion..."
srun apptainer exec --nv -B /tudelft.net/:/tudelft.net/ --pwd ${DATA_PATH} ${SIF_PATH} \
    colmap image_undistorter \
        --image_path ${DATA_PATH}/images \
        --input_path ${DATA_PATH}/sparse_aligned \
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