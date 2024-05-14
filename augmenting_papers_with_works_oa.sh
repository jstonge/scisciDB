#!/bin/bash
#SBATCH --partition=week
#SBATCH --nodes=1
#SBATCH --mem=256G
#SBATCH --time=167:00:00
#SBATCH --job-name=add_papers_to_works_oa2014
#SBATCH --mail-type=ALL

python augmenting_papers_with_works_oa.py 2022
