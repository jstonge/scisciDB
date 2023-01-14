#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --mem=8gb
#SBATCH --time=02:59:59
#SBATCH --job-name=out37
#SBATCH --output=vacc_output/res_37.out 
python get_s2fos_lookup.py --fname=data/split_jsonl_by_nb_of_lines00.jsonl --batch_size=75000