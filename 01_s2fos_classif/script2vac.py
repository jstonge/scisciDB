from pathlib import Path


def main():
    ROOT_DIR = Path()
    METADATA_DIR = ROOT_DIR / "data"
    OUTPUT_DIR = ROOT_DIR / "vacc_output"
    fnames = METADATA_DIR.glob("*jsonl")
    
    if OUTPUT_DIR.exists() == False:
        OUTPUT_DIR.mkdir()

    mem = "8gb"
    wall_time = "02:59:59"
    queue = 'short' if int(wall_time[:2]) < 3 else 'bluemoon'
    
    for i,fname in enumerate(fnames):
        full_script_path = f"combine_folder_{i}.sh"
        with open(full_script_path, "w") as f:
                    f.write(f"#!/bin/bash\n")
                    f.write(f"#SBATCH --partition={queue}\n")
                    f.write(f"#SBATCH --nodes=1\n")
                    f.write(f"#SBATCH --mem={mem}\n")
                    f.write(f"#SBATCH --time={wall_time}\n")
                    f.write(f"#SBATCH --job-name=out{i}\n")
                    f.write(f"#SBATCH --output={OUTPUT_DIR}/res_{i}.out \n")
                    f.write(f"python augment_s2orc_S2FOS.py --fname={str(fname)} --batch_size=75000") 
  
main()