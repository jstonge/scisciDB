#!/bin/bash
#SBATCH --partition=week
#SBATCH --nodes=1
#SBATCH --mem=10G
#SBATCH --time=167:00:00
#SBATCH --job-name=add_papers_to_works_oa
source ~/myconda.sh
conda activate catDB
echo pwd
python src/push_mongodb.py -i data/s2-papers -c s2-papers