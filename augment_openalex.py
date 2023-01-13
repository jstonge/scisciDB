from pathlib import Path

from jsonlines import jsonlines
from tqdm import tqdm


def main():
    """
    Add Open Alex concepts and authorships to s2orc 
    database using on mag_id, doi, or pubmed_id.
    """
    mag_lookup = {}
    doi_lookup = {}
    pmid_lookup = {}
    main_lookup = {}

    print("reading lookups")
    with jsonlines.open(mag_file) as reader:
        for line in tqdm(reader):
            mag_lookup.update(line)
            
    with jsonlines.open(doi_file) as reader:
        for line in tqdm(reader):
            doi_lookup.update(line)
    
    with jsonlines.open(pmid_file) as reader:
        for line in tqdm(reader):
            pmid_lookup.update(line)
    
    with jsonlines.open(main_file) as reader:
        for line in tqdm(reader):
            main_lookup.update(line)

    for file in DIR_METADATA_SIMPLE.glob("*jsonl"):
        print(f"Augmenting {file}")
        with jsonlines.open(file) as reader:
            for line in tqdm(reader):
                
                # find alex_work_id in one of these cases
                if mag_lookup.get(line.get('mag_id')) is not None:
                    alex_work_id = mag_lookup[line.get('mag_id')]
                
                elif doi_lookup.get(line.get('doi')) is not None:
                    alex_work_id = doi_lookup[line.get('doi')]

                elif pmid_lookup.get(line.get('pubmed_id')) is not None:
                    alex_work_id = pmid_lookup[line.get('pubmed_id')]
                
                else:
                    alex_work_id = None
                
                # use alex_work_id to update s2orc with OpenAlex metadata
                if alex_work_id is not None:
                    line.update(main_lookup[alex_work_id])
                    with jsonlines.open(ROOT_DIR / "20200705v1" / 's2orc_gold.jsonl', 'a') as writer:
                        writer.write(line)
                        

if __name__ == "__main__":
    ROOT_DIR = Path()
    DIR_METADATA_SIMPLE = ROOT_DIR / "20200705v1" / "full" / "metadata"
    ALEX_PATH = Path("../openalex/")

    mag_file = ALEX_PATH  / 'mag_lookup.jsonl'
    doi_file = ALEX_PATH  / 'doi_lookup.jsonl'
    pmid_file = ALEX_PATH / 'pmid_lookup.jsonl'
    main_file = ALEX_PATH / 'lookup.jsonl'
    
    main()