"""
Concatenate raw json files from data/s2search_data/{fOS} into
single parquet files of the form `{q}-{fOS}.pqt`

Note that spaces have been replaced by dash and that we only
concatente fOS that does not already have a parquet file in 
input_path.
"""

import argparse
import json
import pathlib
import re
from pathlib import Path

import pandas as pd


def main() -> None:
    
    fOS_Done = [re.sub(('.pqt|computational-'), '', str(_).split("/")[-1]) 
                for _ in  args.input_path.glob("*pqt")]
    
    raw_fOS_dir = [_ for _ in args.input_path.glob("*") 
                   if str(_).endswith('.pqt') == False 
                   and str(_).split("/")[-1] not in fOS_Done]

    for dir in raw_fOS_dir:
        out = []
        # dir = raw_fOS_dir[1]
        fOS = str(dir).split("/")[-1].replace(" ", "-")
        print(fOS)
        for fname in dir.joinpath(args.q).glob("*json"):
            with open(fname) as f:
                d = json.load(f)
                for line in d:
                    out.append(line)
        pd.DataFrame(out)\
          .to_parquet(args.input_path / f"{args.q}-{fOS}.pqt")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-q")
    parser.add_argument("--input_path", type=pathlib.Path)
    args = parser.parse_args()

    main()