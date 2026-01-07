#!/bin/sh

#SBATCH --partition=general # Request partition. Default is 'general'
#SBATCH --qos=short         # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=1:00:00      # Request run time (wall-clock). Default is 1 minute
#SBATCH --ntasks=1          # Request number of parallel tasks per job. Default is 1
#SBATCH --cpus-per-task=4   # Request number of CPUs (threads) per task. Default is 1 (note: CPUs are always allocated to jobs per 2).
#SBATCH --mem=16GB          # Request memory (MB) per node. Default is 1024MB (1GB). For multiple tasks, specify --mem-per-cpu instead
#SBATCH --mail-type=END     # Set mail type to 'END' to receive a mail when the job finishes. 
#SBATCH --output=slurm_%j.out # Set name of output log. %j is the Slurm jobId
#SBATCH --error=slurm_%j.err # Set name of error log. %j is the Slurm jobId

#SBATCH --gres=gpu:a40:1 # Request 1 GPU


# Define the host paths and where they will appear inside the container
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu/SuGaR
DATA_PATH=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu/COLMAP_dataset/south-building
SIF_PATH=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu/containers/sugar.sif

# Measure GPU usage of your job (initialization)
previous=$(/usr/bin/nvidia-smi --query-accounted-apps='gpu_utilization,mem_utilization,max_memory_usage,time' --format='csv' | /usr/bin/tail -n '+2') 

/usr/bin/nvidia-smi # Check sbatch settings are working (it should show the GPU that you requested)

# Load modules
module use /opt/insy/modulefiles
module load cuda/11.8

# Remaining job commands go below here. For example, to run python code that makes use of GPU resources:
## apptainer command
srun --chdir=${REPO_PATH} apptainer exec \
    --nv \
    -B $HOME:$HOME \
    -B /tudelft.net/:/tudelft.net/ \
    ${SIF_PATH} \
    /opt/conda/envs/sugar/bin/python train_full_pipeline.py \
        -s ${DATA_PATH} \
        -r "dn_consistency" \
        --high_poly True \
        --export_obj True

# Measure GPU usage of your job (result)
/usr/bin/nvidia-smi --query-accounted-apps='gpu_utilization,mem_utilization,max_memory_usage,time' --format='csv' | /usr/bin/grep -v -F "$previous"