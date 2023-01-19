"""
Create bash files to run `get_s2fos_lookup` either on the VACC or locally. 
"""

import argparse
import pathlib


def main():
    fnames = args.input_path.glob("*has_abstract.jsonl")
    
    if args.destfile.exists() == False:
        args.destfile.mkdir()

    mem = "8gb"
    wall_time = "02:59:59"
    queue = 'short' if int(wall_time[:2]) < 3 else 'bluemoon'
    
    for i,fname in enumerate(fnames):
        full_script_path = args.destfile / f"combine_folder_{i}.sh"
        with open(full_script_path, "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"#SBATCH --partition={queue}\n")
            f.write(f"#SBATCH --nodes=1\n")
            f.write(f"#SBATCH --mem={mem}\n")
            f.write(f"#SBATCH --time={wall_time}\n")
            f.write(f"#SBATCH --job-name=out{i}\n")
            f.write(f"#SBATCH --output={args.destfile}/res_{i}.out \n")
            f.write(f"python get_s2fos_lookup.py --input_path={str(fname)} \
                                                 --batch_size={args.batch_size} \
                                                 --destfile ../data/s2fos_lookup") 
  
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=pathlib.Path)
    parser.add_argument("--batch_size", type=int)
    parser.add_argument("--destfile", type=pathlib.Path)
    args = parser.parse_args()
    main()