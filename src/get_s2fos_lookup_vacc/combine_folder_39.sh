#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out39
#SBATCH --output=vacc_output/res_39.out 
python get_s2fos_lookup.py --fname=output/metadata_by_decade_all/metadata_1997_simple_has_abstract00.jsonl --batch_size=75000