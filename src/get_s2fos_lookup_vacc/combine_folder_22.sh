#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out22
#SBATCH --output=vacc_output/res_22.out 
python get_s2fos_lookup.py --fname=output/metadata_by_decade_all/metadata_1950_simple_has_abstract.jsonl --batch_size=75000