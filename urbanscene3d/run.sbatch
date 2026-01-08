#!/bin/sh

#SBATCH --partition=general  # Request partition. Default is 'general'
#SBATCH --qos=short          # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=2:30:00       # Request run time (wall-clock) per job.
#SBATCH --ntasks=1           # Request number of parallel tasks per job.
#SBATCH --cpus-per-task=4    # Request number of CPUs (threads) per task.
#SBATCH --mem=32GB           # Request memory per node.
#SBATCH --mail-type=END      # Set mail type to 'END' to receive a mail when the job finishes.

# Set output/error logs
#SBATCH --output=slurm_tnt_%j.out
#SBATCH --error=slurm_tnt_%j.err

# --- Configuration ---
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu
REPO_PATH=${MY_STORAGE}/runs/urbanscene3d
SIF_PATH=${MY_STORAGE}/containers/web_scraper.sif

echo "--- Starting Web Scraping ---"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Running Dataset: TnT"

# --- Command ---
echo "Running command for downloading VCC dataset..."
srun apptainer exec \
    --nv \
    --containall \
    -B /tudelft.net/:/tudelft.net/ \
    --pwd ${REPO_PATH} \
    ${SIF_PATH} \
    /opt/conda/envs/webscraper/bin/python download.py

echo "--- Job finished ---"