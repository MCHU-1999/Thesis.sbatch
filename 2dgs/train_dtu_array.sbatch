#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=short          # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=1:00:00       # Request run time (wall-clock) per job.
#SBATCH --ntasks=1           # Request number of parallel tasks per job.
#SBATCH --cpus-per-task=4    # Request number of CPUs (threads) per task.
#SBATCH --mem=16GB           # Request memory per node.
#SBATCH --mail-type=END      # Set mail type to 'END' to receive a mail when the job finishes.
#SBATCH --gres=gpu:a40:1     # Request 1 GPU per task
#SBATCH --array=0-14         # !!! IMPORTANT: Define array job range. 0 to 14 for 15 scans.

# Set output/error logs to be specific to the array task ID
#SBATCH --output=slurm_dtu_%A_%a.out
#SBATCH --error=slurm_dtu_%A_%a.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/2d-gaussian-splatting
DTU_ROOT=${MY_STORAGE}/DTU
SIF_PATH=${MY_STORAGE}/containers/2dgs.sif

# !!! Define the list of DTU scan folders (15 total)
DTU_SCANS=(
    "scan105" "scan106" "scan110" "scan114" "scan118" "scan122" "scan24" 
    "scan37" "scan40" "scan55" "scan63" "scan65" "scan69" "scan83" "scan97"
)

# !!! Select the current scan based on the array task ID
SCAN_NAME=${DTU_SCANS[$SLURM_ARRAY_TASK_ID]}
DATA_PATH=${DTU_ROOT}/${SCAN_NAME}
OUTPUT_PATH=output/DTU_${SCAN_NAME}

echo "--- Starting DTU Array Job ---"
echo "Job ID: ${SLURM_JOB_ID}, Array Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Training Scan: ${SCAN_NAME}"
echo "Data Path: ${DATA_PATH}"
echo "Output Path: ${OUTPUT_PATH}"

# --- Environment Setup ---
echo "Loading modules..."
module purge
module use /opt/insy/modulefiles
module load cuda/11.8
module load devtoolset/11
module load miniconda/3.11

# Verify environment
echo "Python path: $(which python)"
echo "Python version: $(python --version)"

# Check sbatch settings are working
/usr/bin/nvidia-smi

# --- Training Command ---
echo "Running training command for ${SCAN_NAME}..."
srun --chdir=${REPO_PATH} apptainer exec \
    --nv \
    -B $HOME:$HOME \
    -B /tudelft.net/:/tudelft.net/ \
    ${SIF_PATH} \
    /opt/conda/envs/2DGS/bin/python train.py \
        -s ${DATA_PATH} \
        -m ${OUTPUT_PATH} \
        --disable_viewer

echo "--- Job for ${SCAN_NAME} finished ---"