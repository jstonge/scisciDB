#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out78
#SBATCH --output=vacc_output/res_78.out 
python get_s2fos_lookup.py --fname=data/metadata_2015_simple_has_abstract00.jsonl --batch_size=75000