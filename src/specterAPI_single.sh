#!/bin/bash
#SBATCH --partition=week
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=12:59:59
#SBATCH --job-name=specter

python specterAPI.py --fname computational-Environmental-Science.pqt

