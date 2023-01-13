#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out38
#SBATCH --output=vacc_output/res_38.out 
python augment_s2orc_S2FOS.py --fname=data/metadata_1985_simple_has_abstract.jsonl --batch_size=75000