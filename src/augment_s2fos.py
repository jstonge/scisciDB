"""
Using metadata_{decade}_all.json, we extract papers with abstract.
    
We exclude papers without field of study and year of publication.
"""

import argparse
import json
import pathlib
import re

from jsonlines import jsonlines
from tqdm import tqdm


def main():
    metadata_all_fname = args.input_file
    lookup_dir = args.lookup_dir

    assert metadata_all_fname.endswith("_all.jsonl"), "Only `_all.jsonl` are accepted."
    
    lookup_regex = re.sub('\d_all.jsonl', '*', metadata_all_fname.split("/")[-1])
    lookups = list(lookup_dir.glob(lookup_regex))
    tmpfile = pathlib.Path(re.sub("_all.jsonl", "_tmp.jsonl", metadata_all_fname))

    s2fos_lookup = {}
    
    print(f"Loading {lookup_dir} ({len(lookups)} partitions)")
    
    for file in lookups:
        with open(file) as f:
            s2fos_lookup.update(json.load(f))
    
    print(f"Nb papers with s2fos: {len(s2fos_lookup)}")  

    with jsonlines.open(metadata_all_fname) as reader:
        print(f"Updating lines: {metadata_all_fname}")
        for line in tqdm(reader):
            
            # update current line with s2_fos classification
            line['s2_field_of_study'] = s2fos_lookup.get(line['paper_id'])

            with jsonlines.open(tmpfile, 'a') as writer:
                writer.write(line)
    
    # replace original file with tmpfile
    tmpfile.rename(metadata_all_fname)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help='`metadata_*_all.jsonl` file we want to augmented with s2fos.')
    parser.add_argument("--lookup_dir", type=pathlib.Path)
    args = parser.parse_args()
    

    main()