#!/bin/bash
#SBATCH --partition=week
#SBATCH --nodes=1
#SBATCH --mem=80G
#SBATCH --time=167:00:00
#SBATCH --job-name=add_papers_to_works_oa
source ~/.bashrc
source ~/scisciDB/.venv/bin/activate
python scripts/upload_data.py -i papers -c papers --clean-slate
