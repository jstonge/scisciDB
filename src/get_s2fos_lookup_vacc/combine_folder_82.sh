#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out82
#SBATCH --output=vacc_output/res_82.out 
python get_s2fos_lookup.py --fname=output/metadata_by_decade_all/metadata_2002_simple_has_abstract01.jsonl --batch_size=75000