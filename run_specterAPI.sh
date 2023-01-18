#!/bin/bash

#SBATCH --partition=bluemoon
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=29:59:59
#SBATCH --job-name=specter
python src/query_specterAPI/specterAPI.py --input_path=$1 --output_dir=data/specterAPI