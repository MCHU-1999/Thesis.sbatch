#!/bin/bash
#SBATCH --job-name="dinov3_sidewalk_train"
#SBATCH --partition=gpu-a100
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus-per-task=1
#SBATCH --mem-per-cpu=4G
#SBATCH --account=education-abe-msc-g
#SBATCH --output=logs/train_%j.out
#SBATCH --error=logs/train_%j.err

# Job information
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $(hostname)"
echo "Start Time: $(date)"
echo "=========================================="

# Load modules
echo "Loading modules..."
module purge
module load 2024r1
module load cuda/12.1
module load miniconda3/4.12.0

# Activate conda environment
echo "Activating conda environment..."
conda activate /home/neelabhsingh/.conda/envs/dino_env

# Verify environment
echo "Python: $(which python)"
echo "PyTorch version: $(python -c 'import torch; print(torch._version_)')"

# Navigate to project directory
cd /scratch/neelabhsingh/thesis_project

# Print GPU information
echo "GPU Information:"
nvidia-smi

echo "=========================================="
echo "Starting Training..."
echo "=========================================="

# Run training
python train_sidewalk_segmentation.py \
    --batch-size 8 \
    --epochs 10 \
    --lr 1e-3 \
    --max-size 518

echo "=========================================="
echo "Training Completed!"
echo "End Time: $(date)"
echo "=========================================="