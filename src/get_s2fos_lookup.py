# Description: This script run in batches the s2fos classifier on our personal
#              s2orc database. 
# Author: Jonathan St-Onge

import argparse
import json
import re
import sys
from pathlib import Path

from jsonlines import jsonlines

sys.path.append("s2_fos")
from s2_fos import S2FOS


def batched_classif(path, BATCH_SIZE):
    # path = "output/metadata_by_decade_all/metadata_1971_simple_has_abstract.jsonl"
    # BATCH_SIZE = 75_000
    assert path.endswith("jsonl"), "Only jsonl are accepted."

    out_name = re.sub(".jsonl", "", path.split("/")[-1])
    s2ranker = S2FOS("s2_fos/data")
    
    lookup = {}
    
    with jsonlines.open(path) as reader:
        current_batch = []
        batch_counter = 0
        i = 0      

        for line in reader:
            if i <= BATCH_SIZE:
                # keep appending until we reach batch size
                current_batch.append(line)
                i += 1
            else:
                
                print(f"Batch: {batch_counter}")
                # make predictions
                preds = s2ranker.predict(current_batch)
                
                # update lookup
                for paper, pred in zip(current_batch, preds):
                    mag_field = [{ 'category': c, 'source': 'mag' } for c in paper['mag_field']]
                    s2fos_field = [{ 'category': c, 'source': "s2-fos-model" } for c in pred ]
                    lookup[paper['paper_id']] =  mag_field + s2fos_field 

                # reset counter values
                current_batch = []
                i = 0
                # add one batch done
                batch_counter += 1
    
    # one last batch for the road
    preds = s2ranker.predict(current_batch)
    
    for paper, pred in zip(current_batch, preds):
        mag_field = [{ 'category': c, 'source': 'mag' } for c in paper['mag_field']]
        s2fos_field = [{ 'category': c, 'source': "s2-fos-model" } for c in pred ]
        lookup[paper['paper_id']] =  mag_field + s2fos_field
    
    with open(DIR_OUTPUT / f"{out_name}_lookup.jsonl", 'w') as f:
        json.dump(lookup, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--fname")
    parser.add_argument("--batch_size", type=int)
    args = parser.parse_args()
    
    DIR_ROOT = Path()
    DIR_OUTPUT = DIR_ROOT / "output" / "s2fos_lookup"

    batched_classif(args.fname, BATCH_SIZE=args.batch_size)
