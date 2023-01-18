import argparse
import pathlib
import re
from pathlib import Path


def main():
    if args.input_file.exists():
        with open(args.o / "run_specter_on_vacc.sh", "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"#SBATCH --partition=bluemoon\n")
            f.write(f"#SBATCH --nodes=1\n")
            f.write(f"#SBATCH --mem=8gb\n")
            f.write(f"#SBATCH --time=29:59:59\n")
            f.write(f"#SBATCH --job-name=specter\n")
            f.write(f"python src/query_specterAPI/specterAPI.py --input_path={args.input_file} --output_dir=data/specterAPI") 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=pathlib.Path, help="Parquet file produced in query_s2searchAPI for which we want specter embeddings")
    parser.add_argument("-o", type=pathlib.Path)
    args = parser.parse_args()
    main()