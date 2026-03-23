#!/bin/sh

#SBATCH --partition=general
#SBATCH --qos=short
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32GB
#SBATCH --mail-type=END
#SBATCH --gres=gpu:a40:1

#SBATCH --output=slurm_DA3_seq_%j.out
#SBATCH --error=slurm_DA3_seq_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/PlanarSplatting
SIF_PATH=${MY_STORAGE}/containers/planarsplatting.sif

# Define arrays for names and paths
SCENES=("box" "SimpleHouse2" "scan24" "scan40")
PATHS=(
    "${MY_STORAGE}/synthetic/box"
    "${MY_STORAGE}/synthetic/SimpleHouse2"
    "${MY_STORAGE}/DTU/scan24"
    "${MY_STORAGE}/DTU/scan40"
)

# --- Environment Setup ---
module purge
module use /opt/insy/modulefiles
module load cuda/12.1
module load devtoolset/11
module load miniconda/3.11

echo "--- Starting Seq Training Job ---"

# --- Seq Loop ---
# This loop iterates from index 0 to 5
for i in ${!SCENES[@]}; do
    DATA_PATH=${PATHS[$i]}
    CURRENT_SCENE=${SCENES[$i]}

    echo "***********************************************"
    echo "Processing Scene: ${CURRENT_SCENE}"
    echo "Path: ${DATA_PATH}"
    echo "Start Time: $(date)"
    echo "***********************************************"

    srun apptainer exec \
        --nv \
        --containall \
        -B /tudelft.net/:/tudelft.net/ \
        --pwd ${REPO_PATH} \
        ${SIF_PATH} \
        /opt/conda/envs/planarSplatting/bin/python run_DA3.py \
            --data_path ${DATA_PATH} \
            --exp_name ${CURRENT_SCENE} \
            --conf_path configs/DA3.conf

    echo "Finished ${CURRENT_SCENE} at $(date)"
done

echo "--- All 5 scenes finished ---"