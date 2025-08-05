#!/bin/bash -l
#SBATCH --account=lpt2_sysadmin

module purge &> /dev/null
module load Python/3.11.5-GCCcore-13.2.0

which python
