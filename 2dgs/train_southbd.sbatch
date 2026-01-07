#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=short          # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=2:00:00       # Request run time (wall-clock) per job.
#SBATCH --ntasks=1           # Request number of parallel tasks per job.
#SBATCH --cpus-per-task=4    # Request number of CPUs (threads) per task.
#SBATCH --mem=16GB           # Request memory per node.
#SBATCH --mail-type=END      # Set mail type to 'END' to receive a mail when the job finishes.
#SBATCH --gres=gpu:a40:1     # Request 1 GPU per task

# Set output/error logs
#SBATCH --output=slurm_south_building_%j.out
#SBATCH --error=slurm_south_building_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/2d-gaussian-splatting
DATA_PATH=${MY_STORAGE}/COLMAP_dataset/south-building
OUTPUT_PATH=output/south_building
SIF_PATH=${MY_STORAGE}/containers/2dgs.sif

echo "--- Starting 2DGS Training Job ---"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Training Dataset: south-building"
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
echo "Running training command for south-building..."
srun --chdir=${REPO_PATH} apptainer exec \
    --nv \
    -B $HOME:$HOME \
    -B /tudelft.net/:/tudelft.net/ \
    ${SIF_PATH} \
    /opt/conda/envs/2DGS/bin/python train.py \
        -s ${DATA_PATH} \
        -m ${OUTPUT_PATH}

echo "--- Training job finished ---"