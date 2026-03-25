#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=short          # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=1:00:00       # Request run time (wall-clock) per job.
#SBATCH --ntasks=1           # Request number of parallel tasks per job.
#SBATCH --cpus-per-task=4    # Request number of CPUs (threads) per task.
#SBATCH --mem=16GB           # Request memory per node.
#SBATCH --mail-type=END      # Set mail type to 'END' to receive a mail when the job finishes.
#SBATCH --gres=gpu:a40:1     # Request 1 GPU per task

# Set output/error logs
#SBATCH --output=slurm_inference_%j.out
#SBATCH --error=slurm_inference_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/DA3
SIF_PATH=${MY_STORAGE}/containers/da3.sif
# DATA_PATH=${MY_STORAGE}/synthetic/box
# DATA_PATH=${MY_STORAGE}/synthetic/SimpleHouse2
# DATA_PATH=${MY_STORAGE}/DTU/scan24
# DATA_PATH=${MY_STORAGE}/DTU/scan40
# DATA_PATH=${MY_STORAGE}/TNT_GOF/TrainingSet/Barn


echo "--- Starting DA3 Job ---"
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

export TORCH_HOME=${MY_STORAGE}/.cache
export APPTAINERENV_TORCH_HOME=${MY_STORAGE}/.cache
export APPTAINERENV_LD_LIBRARY_PATH="/usr/lib64:${LD_LIBRARY_PATH}"
export APPTAINERENV_HF_HOME=${MY_STORAGE}/.cache/huggingface
export APPTAINERENV_HF_HUB_CACHE=${MY_STORAGE}/.cache/huggingface/hub
export APPTAINERENV_TRANSFORMERS_CACHE=${MY_STORAGE}/.cache/huggingface/hub

# --- Training Command ---
echo "Running command..."

srun apptainer exec \
    --nv \
    --containall \
    -B /tudelft.net/:/tudelft.net/ \
    --pwd ${REPO_PATH} \
    ${SIF_PATH} \
    bash -lc "
set -e
echo 'Installing DA3...'
/opt/conda/envs/DA3/bin/pip install -e . 

for DATA_PATH in \
    ${MY_STORAGE}/DTU/scan24 \
    ${MY_STORAGE}/DTU/scan40
do
    echo \"Running DA3 on \${DATA_PATH}...\"
    /opt/conda/envs/DA3/bin/python run_da3_simple.py --data_dir \"\${DATA_PATH}\"
done
"
echo "--- Job finished ---"