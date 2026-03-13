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
#SBATCH --output=slurm_DA3_%j.out
#SBATCH --error=slurm_DA3_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/PlanarSplatting
SIF_PATH=${MY_STORAGE}/containers/planarsplatting.sif
DATA_PATH=${MY_STORAGE}/synthetic/SimpleHouse
# DATA_PATH=${MY_STORAGE}/TNT_GOF/TrainingSet/Barn
DATA_PATH=${MY_STORAGE}/DTU/scan24

echo "--- Starting PlanarSplatting Training Job ---"
echo "Job ID: ${SLURM_JOB_ID}"

# --- Environment Setup ---
echo "Loading modules..."
module purge
module use /opt/insy/modulefiles
module load cuda/12.1
module load devtoolset/11
module load miniconda/3.11

# Verify environment
echo "Python path: $(which python)"
echo "Python version: $(python --version)"

# Check sbatch settings are working
/usr/bin/nvidia-smi
ulimit -n 60000

# --- Training Command ---
echo "Running command..."
srun apptainer exec \
    --nv \
    --containall \
    -B /tudelft.net/:/tudelft.net/ \
    --pwd ${REPO_PATH} \
    ${SIF_PATH} \
    /opt/conda/envs/planarSplatting/bin/python run_DA3.py \
        --data_path ${DATA_PATH} \
        --init_plane_num 2000 \
        --scene_bounding_sphere 6 \
        --max_total_iters 5000 \
        --coarse_stage_ite 500 \
        --split_start_ite 1000 \
        --exp_name DTU_scan24 \
        --conf_path utils_demo/demo_DA3.conf \

echo "--- Job finished ---"