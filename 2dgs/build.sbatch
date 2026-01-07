#!/bin/sh

#SBATCH --partition=general # Request partition. Default is 'general'
#SBATCH --qos=short         # Request Quality of Service. Default is 'short' (maximum run time: 4 hours)
#SBATCH --time=3:00:00      # Request run time (wall-clock). Default is 1 minute
#SBATCH --ntasks=1          # Request number of parallel tasks per job. Default is 1
#SBATCH --cpus-per-task=8   # Request number of CPUs (threads) per task. Default is 1 (note: CPUs are always allocated to jobs per 2).
#SBATCH --mem=16GB          # Request memory (MB) per node. Default is 1024MB (1GB). For multiple tasks, specify --mem-per-cpu instead
#SBATCH --mail-type=END     # Set mail type to 'END' to receive a mail when the job finishes. 
#SBATCH --output=build_%j.out # Set name of output log. %j is the Slurm jobId
#SBATCH --error=build_%j.err # Set name of error log. %j is the Slurm jobId


# Define the host paths and where they will appear inside the container
MY_STORAGE=/tudelft.net/staff-umbrella/Deep3D/mingchiehhu

# Remaining job commands go below here. 
srun --chdir=${MY_STORAGE}/containers apptainer build --fakeroot 2dgs.sif 2dgs.def 
