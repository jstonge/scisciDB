#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out21
#SBATCH --output=vacc_output/res_21.out 
python get_s2fos_lookup.py --fname=output/metadata_by_decade_all/metadata_2016_simple_has_abstract02.jsonl --batch_size=75000