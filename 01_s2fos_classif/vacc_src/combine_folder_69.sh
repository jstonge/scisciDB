#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out69
#SBATCH --output=vacc_output/res_69.out 
python augment_s2orc_S2FOS.py --fname=data/metadata_2005_simple_has_abstract02.jsonl --batch_size=75000