#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=50gb
#SBATCH --time=02:59:59
#SBATCH --job-name=top2vec

python src/embeddings2hdbscan.py --input_dir data/specter --N_REP 20000 --N_comp 2
