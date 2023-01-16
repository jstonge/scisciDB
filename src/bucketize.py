"""
We sort and bucketize s2orc `metadata/` by decade.
"""
import argparse
import pathlib

from jsonlines import jsonlines
from tqdm import tqdm


def main():

    if args.output_dir.exists() is False: args.output_dir.mkdir()

    with jsonlines.open(args.input_file) as reader:
        for line in tqdm(reader):
            if line.get('year') is not None:
                decade = line['year'] - line['year'] % 10
                if (decade >= 1950) and (line['year'] <= 2022):
                    OUT = args.output_dir / f'metadata_{decade}_all.jsonl'
                    with jsonlines.open(OUT, 'a') as writer:
                        writer.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file")
    parser.add_argument("--output_dir", type=pathlib.Path)
    args = parser.parse_args()
    main()