import argparse
import csv
import pathlib
import re
from pathlib import Path

import numpy as np
import pandas as pd
from jsonlines import jsonlines


def main():
    specter_fnames = list(specterAPI_DIR.glob("*json"))
    
    # I/O metadata
    meta_embedding_out.unlink(missing_ok=True) # delete file if exists
    tsvfile = open(meta_embedding_out, "a", newline='')
    writer = csv.writer(tsvfile, delimiter="\t")
    cols = ['paperId', 'title', 'abstract', 'year', 'venue', 'citationCount']
    
    for i, fname in enumerate(specter_fnames):
        print(f"{i} / {len(specter_fnames)} done.")
        embedding_dat = []
        field = re.sub("(computational-|.json)", "", str(fname).split("/")[-1])

        metadata_lookup = pd.read_parquet(s2search_DIR / f'computational-{field}.pqt', columns=cols)\
                            .drop_duplicates(subset='paperId')\
                            .set_index('paperId')\
                            .to_dict(orient='index')

        with jsonlines.open(fname) as reader:
            for paper in reader:
                #!TODO: unclear why we have paper without corresponding metadata
                p_id = paper['paperId']
                if paper['embedding'] is not None and metadata_lookup.get(p_id) is not None:
                    # save the metadata as we go along
                    writer.writerow([p_id] + list(metadata_lookup[p_id].values()) + [field])
                    embedding_dat.append(paper['embedding']['vector'])

        # save the embeddings keeping track of the order to make sure it
        # follows the metadata
        np.save(OUT_DIR / f"embeddings_{i}", np.matrix(embedding_dat))
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=pathlib.Path)
    parser.add_argument("--output_dir", type=pathlib.Path)
    args = parser.parse_args()

    s2search_DIR = args.data_dir / 's2search_data'
    specterAPI_DIR = args.data_dir / 'specterAPI'
    OUT_DIR = args.data_dir / 'specter'

    meta_embedding_out = args.output_dir / 'meta_embeddings.tsv'

    main()