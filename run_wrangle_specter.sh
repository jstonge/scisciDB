#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=32gb
#SBATCH --time=02:59:59
#SBATCH --job-name=top2vec

python src/wrangle_specter.py --data_dir data --output_dir data/specter
