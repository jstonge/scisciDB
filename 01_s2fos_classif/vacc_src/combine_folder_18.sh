#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out18
#SBATCH --output=vacc_output/res_18.out 
python augment_s2orc_S2FOS.py --fname=data/metadata_2012_simple_has_abstract03.jsonl --batch_size=75000