import argparse
import re
from pathlib import Path

from jsonlines import jsonlines


def main():
    
    # We expect fname to be of the form ../../metadata_{decade}_simple_has_abstract.jsonl
    assert len(args.path.split("/")) == 3, "Wrong format"
    fname = args.path.split("/")[-1]
    assert len(fname.split("_")) == 5, "Wrong format"
    decade = int(fname.split("_")[1])

    with jsonlines.open(args.path) as reader:
        out = {}
        for line in reader:
            yr = line['year']

            if out.get(yr) is None:
                out[yr] = [ line ]
            else:
                out[yr] += [ line ]
                
            for k in out.keys():
                yearly_fname = re.sub(str(decade), str(k), str(fname))
                # We want to write to current dir
                yearly_fname = yearly_fname.split("/")[-1]
                for line in out[k]:
                    with jsonlines.open(yearly_fname, mode='a') as writer:
                        writer.write(line)
                
                out = {}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    args = parser.parse_args()
    

    main()
