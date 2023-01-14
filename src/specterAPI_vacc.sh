#!/bin/bash
#SBATCH --partition=week
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=167:59:59
#SBATCH --job-name=specter

for f in *pqt; do python specterAPI.py --fname $f; done

