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
#SBATCH --output=slurm_tnt_pgsr_%j.out
#SBATCH --error=slurm_tnt_pgsr_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/PlanarSplatting
SIF_PATH=${MY_STORAGE}/containers/planarsplatting.sif
DATA_PATH=${MY_STORAGE}/TNT_GOF/TrainingSet/Barn
GEO_DATA_PATH=${MY_STORAGE}/PGSR/output_tnt/Barn/test/train/ours_30000
INIT_MESH_PATH=${MY_STORAGE}/PGSR/output_tnt/Barn/test/mesh/tsdf_fusion_post.ply

echo "--- Starting PlanarSplatting Training Job ---"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Running Dataset: TnT"

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
echo "Running command for TnT..."
srun apptainer exec \
    --nv \
    --containall \
    -B /tudelft.net/:/tudelft.net/ \
    --pwd ${REPO_PATH} \
    ${SIF_PATH} \
    /opt/conda/envs/planarSplatting/bin/python run_tnt_w_mesh.py \
        --data_path ${DATA_PATH} \
        --init_mesh ${INIT_MESH_PATH} \
        --init_plane_num 2000 \
        --scene_bounding_sphere 6 \
        --max_total_iters 20000 \
        --coarse_stage_ite 5000 \
        --split_start_ite 6000 \
        --exp_name meshbased_run1

echo "--- Job finished ---"