#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=medium         # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=5:00:00       # Request run time (wall-clock) per job.
#SBATCH --ntasks=1           # Request number of parallel tasks per job.
#SBATCH --cpus-per-task=4    # Request number of CPUs (threads) per task.
#SBATCH --mem=64GB           # Request memory per node.
#SBATCH --mail-type=END      # Set mail type to 'END' to receive a mail when the job finishes.
#SBATCH --gres=gpu:a40:1     # Request 1 GPU per task

# Set output/error logs
#SBATCH --output=slurm_prep_tnt_%j.out
#SBATCH --error=slurm_prep_tnt_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/dn-splatter
SIF_PATH=${MY_STORAGE}/containers/dnsplatter.sif
DATA_PATH=${MY_STORAGE}/TNT_GOF/TrainingSet

# Define the 6 scenes to be processed
SCENES=('Courthouse' 'Truck' 'Caterpillar' 'Barn' 'Meetingroom' 'Ignatius')

echo "--- Starting dn-splatter Data Preparation Job ---"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Processing Dataset: TnT"

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

export TORCH_HOME=${MY_STORAGE}/.cache
export APPTAINERENV_TORCH_HOME=${MY_STORAGE}/.cache

# --- Data Preparation Commands ---
echo "Running data preparation for all scenes in TnT..."

for scene in "${SCENES[@]}"; do
    echo "--- Processing scene: ${scene} ---"

    # Define scene-specific data path
    SCENE_DATA_PATH="${DATA_PATH}/${scene}"

    # Generate and Align Depth Maps
    # echo "Step 1: Generating and aligning depth maps for ${scene}..."
    # srun apptainer exec \
    #     --nv \
    #     --containall \
    #     -B /tudelft.net/:/tudelft.net/ \
    #     --pwd ${REPO_PATH} \
    #     ${SIF_PATH} \
    #     python dn_splatter/scripts/align_depth.py \
    #         --data ${SCENE_DATA_PATH}

    # Generate Normal Maps
    echo "Step 2: Generating normal maps for ${scene}..."
    srun apptainer exec \
        --nv \
        --containall \
        -B /tudelft.net/:/tudelft.net/ \
        --pwd ${REPO_PATH} \
        ${SIF_PATH} \
        python dn_splatter/scripts/normals_from_pretrain.py \
            --data-dir ${SCENE_DATA_PATH} \
            --resolution low

    echo "--- Finished processing scene: ${scene} ---"
done

echo "--- All data preparation jobs finished ---"