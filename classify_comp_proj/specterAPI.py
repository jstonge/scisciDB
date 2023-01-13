import argparse
from pathlib import Path
import requests
import re
from tqdm import tqdm
from time import sleep

from jsonlines import jsonlines
import pandas as pd

def _specter_via_api(paperId:str, fout:Path) -> None:
    """
    helper function to query semantic scholar's Paper API 

    params
    ======
      - paperId: paperID
      - field: field of study

    Note
    ====
      - Note that our API rate limit is 100 req/sec
    """
    header = { "x-api-key" : '8mH99xWXoi60vMDfkSJtb6zVhSLiSgNP8ewg3nlZ' }
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paperId}"
    fields_papers = "externalIds,isOpenAccess,publicationVenue,publicationTypes,publicationDate,journal,embedding,tldr"
    fields_author = "authors.affiliations,authors.homepage,authors.hIndex,authors.citationCount,authors.aliases,authors.externalIds"
    url = f"{base_url}?fields={fields_papers},{fields_author}"
    
    try:
        r = requests.get(url, headers = header)
  
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    if r.status_code == 200:
        with jsonlines.open(fout, "a") as writer: 
            writer.write(r.json())
    else:
        return r.status_code

def main():
    paperIds = set(pd.read_parquet(DAT_DIR / args.fname).paperId)
    field = re.sub(".pqt", "", args.fname)
    print(f"Doing {field} ({len(paperIds)} papers)")

    outname = OUTPUT_DIR_FIELD / f"{field}.json"

    already_done = []
    if outname.exists():
        with jsonlines.open(outname) as f:
            for line in f:
                already_done.append(line)

        already_done = set([paper['paperId'] for paper in already_done])
        
        paperIds = paperIds - already_done

    counter = 0
    for paperid in tqdm(paperIds):
        _specter_via_api(paperid, outname)
        
        counter += 1 

        if counter == 100:
            sleep(1)
            counter = 0

if __name__ == '__main__':
    CURRENT_DIR = Path()
    DAT_DIR = CURRENT_DIR / 'raw_dat'
    OUTPUT_DIR_FIELD = CURRENT_DIR / 'specter'

    parser = argparse.ArgumentParser()
    parser.add_argument("--fname")
    args = parser.parse_args()

    main()