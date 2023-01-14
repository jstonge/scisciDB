#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out29
#SBATCH --output=vacc_output/res_29.out 
python get_s2fos_lookup.py --fname=output/metadata_by_decade_all/metadata_1977_simple_has_abstract.jsonl --batch_size=75000