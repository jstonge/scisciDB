from pathlib import Path

from jsonlines import jsonlines
from tqdm import tqdm

def main():
    """
    We sort and bucketize s2orc `metadata/` by decade.
    """
    S2ORC_DIR = Path()
    DIR_METADATA = S2ORC_DIR / "20200705v1" / "full" / "metadata"
    OUTPUT_DIR   = S2ORC_DIR / "metadata_by_decade_all"

    if OUTPUT_DIR.exists() is False: OUTPUT_DIR.mkdir()
    
    files = list(DIR_METADATA.glob("*jsonl"))
    for i, f in enumerate(files):
        print(f'Done {i+1}/{len(files)} files')
        with jsonlines.open(f) as reader:
            for line in tqdm(reader):
                if line.get('year') is not None:
                    decade = line['year'] - line['year'] % 10
                    if (decade >= 1950) and (line['year'] <= 2022):
                        OUT = OUTPUT_DIR / f'metadata_{decade}_all.jsonl'
                        with jsonlines.open(OUT, 'a') as writer:
                            writer.write(line)

if __name__ == '__main__':
    main()
