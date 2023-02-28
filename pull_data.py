"""
Grab urls from semantic scholar, then save those who already done into a csv file.
We assume that a url has been done when we already successfully unzip the downloaded file.
"""

import re
import sys
from pathlib import Path

import pandas as pd
import requests

from creds import s2orc_token

if __name__ == "__main__":
    root_dir = Path()

    # corpus = 'citations'
    corpus = sys.argv[1]
    header = { "x-api-key" : f'{s2orc_token}' }
    base_url = f"https://api.semanticscholar.org/datasets/v1/release/2023-01-31/dataset/{corpus}"
    r = requests.get(base_url, headers = header)
    
    links = r.json()['files'] if r.json().get('files') is not None else []
    short_link=["".join(re.split("(/|.gz)", link)[12:14]) for link in links]
    
    # if still a gz after trying to unzip it, with assume the download did not work 
    done_short_url = set([str(_).split("/")[-1]+".gz" 
                          for _ in root_dir.joinpath(corpus).glob("20230203*") 
                          if str(_).endswith('gz') == False])

    df = pd.DataFrame({"url":links, "short_url":short_link})
    df = df[~df.short_url.isin(done_short_url)]
    output_file = root_dir / corpus / f"2023-01-31_{corpus}.csv"
    output_file.unlink(missing_ok=True)
    df.to_csv(output_file, index=False, header=False)