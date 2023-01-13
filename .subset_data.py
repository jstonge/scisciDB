from jsonlines import jsonlines
from pathlib import Path
import argparse

S2ORC_DIR = Path()
DIR_METADATA   = S2ORC_DIR / "metadata_by_decade_all"

parser = argparse.ArgumentParser()
parser.add_argument("--fname")
parser.add_argument("--batch_size", type=int)
args = parser.parse_args()

with jsonlines.open(DIR_METADATA / args.fname) as reader:
        for i,obj in enumerate(reader):
            if i < args.batch_size:
                with jsonlines.open(DIR_METADATA / f'test_{args.batch_size}.jsonl', mode='a') as writer:
                    writer.write(obj)
            else:
                break
