import re
import sys

import pandas as pd
import requests

header = { "x-api-key" : '8mH99xWXoi60vMDfkSJtb6zVhSLiSgNP8ewg3nlZ' }
base_url = f"https://api.semanticscholar.org/datasets/v1/release/2023-01-31/dataset/{sys.argv[1]}"
r = requests.get(base_url, headers = header)

links = r.json()['files']
short_link=["".join(re.split("(/|.gz)", link)[12:14]) for link in links]

pd.DataFrame({"url":links, "short_url":short_link}).to_csv(f"2023-01-31_{sys.argv[1]}.csv", index=False, header=False)
