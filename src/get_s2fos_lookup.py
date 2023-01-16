"""
Run s2fos classifier on s2orc, in batches. 
"""

import argparse
import json
import pathlib
import re
import sys

from jsonlines import jsonlines

sys.path.append("s2_fos")
from s2_fos import S2FOS


def main():

    assert args.input_path.endswith("jsonl"), "Only jsonl are accepted."

    if args.destfile.exists() == False: args.destfile.mkdir()

    out_name = re.sub(".jsonl", "", args.input_path.split("/")[-1])
    s2ranker = S2FOS("s2_fos/data")
    
    lookup = {}
    
    with jsonlines.open(args.input_path) as reader:
        current_batch = []
        batch_counter = 0
        i = 0      

        for line in reader:
            if i <= args.batch_size:
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
    
    with open(args.destfile / f"{out_name}_lookup.jsonl", 'w') as f:
        json.dump(lookup, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path")
    parser.add_argument("--batch_size", type=int)
    parser.add_argument("--destfile", type=pathlib.Path)
    args = parser.parse_args()

    main()
