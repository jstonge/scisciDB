import argparse
import json
import re
from pathlib import Path

from jsonlines import jsonlines
from tqdm import tqdm

def main():
    """
    Using metadata_{decade}_all.json, we extract papers with abstract.
    
    We exclude papers without field of study and year of publication.
    """
    S2ORC_DIR = Path()
    DIR_METADATA   = S2ORC_DIR / "output" / "metadata_by_decade_all"
    DIR_S2FOS = S2ORC_DIR / 'output' / 's2_lookup'

    s2fos_lookup = {}
    
    # lookups = list(DIR_S2FOS.glob("metadata_201*"))
    lookups = list(DIR_S2FOS.glob(args.lookup))
    print(f"Loading {args.lookup} ({len(lookups)} partitions)")
    for file in lookups:
        with open(file) as f:
            s2fos_lookup.update(json.load(f))
    
    print(f"Nb papers with s2fos: {len(s2fos_lookup)}")

    # decade = 2010
    print(f"Chosen decade: {args.decade}")
    fname = [_ for _ in DIR_METADATA.glob("*.jsonl")
             if re.search(f"metadata_{args.decade}_all.jsonl", str(_))][0]
    
    fname_short = re.sub(".jsonl", "", str(fname).split("/")[-1])+'_tmp'+'.jsonl'

    with jsonlines.open(fname) as reader:
        print(f"Updating lines: {fname}")
        for line in tqdm(reader):
            
            # update current line with s2_fos classification
            line['s2_field_of_study'] = s2fos_lookup.get(line['paper_id'])

            with jsonlines.open(DIR_METADATA / fname_short, 'a') as writer:
                writer.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--decade", type=int)
    parser.add_argument("--lookup")
    args = parser.parse_args()
    

    main()