#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out43
#SBATCH --output=vacc_output/res_43.out 
python get_s2fos_lookup.py --fname=output/metadata_by_decade_all/metadata_1984_simple_has_abstract.jsonl --batch_size=75000