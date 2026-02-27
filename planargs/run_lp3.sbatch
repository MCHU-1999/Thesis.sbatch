#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=short          # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=1:00:00       # Request run time (wall-clock) per job.
#SBATCH --ntasks=1           # Request number of parallel tasks per job.
#SBATCH --cpus-per-task=4    # Request number of CPUs (threads) per task.
#SBATCH --mem=32GB           # Request memory per node.
#SBATCH --mail-type=END      # Set mail type to 'END' to receive a mail when the job finishes.
#SBATCH --gres=gpu:a40:1     # Request 1 GPU per task

# Set output/error logs
#SBATCH --output=slurm_lp3_%j.out
#SBATCH --error=slurm_lp3_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/PlanarGS
SIF_PATH=${MY_STORAGE}/containers/planargs.sif
DATA_PATH=${MY_STORAGE}/TNT_GOF/TrainingSet/Barn

echo "--- Starting PlanarGS Job ---"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Training Dataset: TnT"

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
ulimit -n 60000

# Define a directory on your staff-umbrella or project storage
export HF_HOME=${MY_STORAGE}/.cache/huggingface
export TRANSFORMERS_CACHE=${MY_STORAGE}/.cache/huggingface

# --- Training Command ---
echo "Running training command for TnT..."
srun apptainer exec \
    --nv \
    --containall \
    -B /tudelft.net/:/tudelft.net/ \
    --pwd ${REPO_PATH} \
    --env QT_QPA_PLATFORM=offscreen \
    ${SIF_PATH} \
    /opt/conda/envs/planargs/bin/python run_lp3.py \
        -s ${DATA_PATH}\
        -t "wall. door. window. roof"\
        --vis

echo "--- Training job finished ---"