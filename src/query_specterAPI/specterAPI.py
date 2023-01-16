"""
Query specterAPI from semantic scholar for papers in a selected parquet file. 

The script will look if the file already exists, and if so, only ask for papers
not already in it.
"""

import argparse
import pathlib
import re
from pathlib import Path
from time import sleep

import pandas as pd
import requests
from jsonlines import jsonlines
from tqdm import tqdm


def _specter_via_api(paperId: str, fout: Path) -> None:
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
    header = {"x-api-key": "8mH99xWXoi60vMDfkSJtb6zVhSLiSgNP8ewg3nlZ"}
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paperId}"
    fields_papers = "externalIds,isOpenAccess,publicationVenue,publicationTypes,publicationDate,journal,embedding,tldr"
    fields_author = "authors.affiliations,authors.homepage,authors.hIndex,authors.citationCount,authors.aliases,authors.externalIds"
    url = f"{base_url}?fields={fields_papers},{fields_author}"

    try:
        r = requests.get(url, headers=header)

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if r.status_code == 200:
        with jsonlines.open(fout, "a") as writer:
            writer.write(r.json())
    else:
        return r.status_code


def main():
    paperIds = set(pd.read_parquet(args.input_path).paperId)
    field = re.sub(".pqt", "", args.input_path.split("/")[-1])
    print(f"Doing {field} ({len(paperIds)} papers)")

    outname = args.output_dir / f"{field}.json"

    already_done = []
    if outname.exists():
        with jsonlines.open(outname) as f:
            for line in f:
                already_done.append(line)

        already_done = set([paper["paperId"] for paper in already_done])

        paperIds = paperIds - already_done

    if len(paperIds) > 0:
        counter = 0
        for paperid in tqdm(paperIds):
            _specter_via_api(paperid, outname)
            counter += 1
            if counter == 100:
                sleep(1)
                counter = 0


if __name__ == "__main__":
    CURRENT_DIR = Path()
    OUTPUT_DIR_FIELD = CURRENT_DIR / "output" / "specter"

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", help="Parquet file produced in query_s2searchAPI")
    parser.add_argument("--output_dir", type=pathlib.Path)
    args = parser.parse_args()

    main()
