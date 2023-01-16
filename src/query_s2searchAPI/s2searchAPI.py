"""
Query the semantic scholar api for a particular field.

The field used here are s2_fields, contrary to the s2orc database.
Meaning if we want to normalize by field we need to have the total
number of papers in a year according to s2_fos model.

Also We hardcoded the range to be between 1950 and 2022.

If the script fails, we need to fix manually.
"""
import argparse
import json
import pathlib
import re
from pathlib import Path
from time import sleep

import pandas as pd
import requests


def get_fOS_done():
    s2FOS_stem = set(["Chemistry", "Biology", "Materials Science", "Computer Science", "Physics","Geology", "Mathematics", "Engineering", "Environmental Science"])
    s2FOS_soc_sci = set(["Psychology", "Linguistics", "Political Science","Economics", "Philosophy", "Art","History","Geography","Sociology"])
    s2FOS_misc = set(["Medicine", "Law", "Business", "Agricultural and Food Sciences", "Education"])

    s2FOS = s2FOS_stem | s2FOS_soc_sci | s2FOS_misc

    fOS_done = set()
    for dir in Path("../../data/s2search_data/").glob("*"):
        year_done = [int(re.findall("^\d{4}", str(_).split("/")[-1])[0]) 
                     for _ in dir.glob(f"{args.q}/*")]
        if min(year_done) <= 1960 and max(year_done) >= 2015:
            fOS_done.add(str(dir).split("/")[-1])

    return s2FOS - fOS_done


def _s2search_via_api(q:str, fOS:str, yr:int, off:int) -> None:
    """
    helper function to query semantic scholar's Search for papers by keyword API 

    params
    ======
      - q: query
      - fOS: (sem scholar field Of Study
      - yr: year
      - off: offset

    Note
    ====
      - The output file is of the form: DIR / s2search_data / fOS / q / {yr}_{off}.json
      - The overall limit seems to be 10K articles. If we fine grained our query by year,
        the only field that suffers from the limit for the `computational` is physics.
    """
    header = { "x-api-key" : '8mH99xWXoi60vMDfkSJtb6zVhSLiSgNP8ewg3nlZ' }
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = "url,abstract,authors,title,venue,journal,year,citationCount,influentialCitationCount,referenceCount,fieldsOfStudy,s2FieldsOfStudy"
    url = f"{base_url}?year={yr}&fieldsOfStudy={fOS}&query={q}&fields={fields}&offset={off}&limit=100"
    
    OUTPUT_DIR_FIELD = args.output_dir / args.fOS
    OUTPUT_DIR_QUERY = OUTPUT_DIR_FIELD / q
    
    if OUTPUT_DIR_FIELD.exists() == False: OUTPUT_DIR_FIELD.mkdir()
    if OUTPUT_DIR_QUERY.exists() == False: OUTPUT_DIR_QUERY.mkdir()

    try:
        r = requests.get(url, headers = header)
  
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    if r.status_code == 200:
        with open(OUTPUT_DIR_QUERY / f"{yr}_{off}.json", "a") as f: 
            json.dump(r.json()["data"], f)
    else:
        return r.status_code

def main():

    print(f"Doing: {args.fOS}")
    
    S2_OFFSET_LIMIT = 100
    S2_LIMIT = 10_000
    
    for year in range(1950,2022):
        print(f"Doing year {year}")
        i = 0
        sc = None
        while (i <= S2_LIMIT) and (sc is None):
            sc = _s2search_via_api(args.q, args.fOS, year, i)
            i += S2_OFFSET_LIMIT # the offset limit
            sleep(0.1)
        
        sleep(0.2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", help="Query to s2SearchAPI")
    parser.add_argument("--fOS", help="s2FieldsOfStudy, see https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/get_graph_get_paper_search")
    parser.add_argument("--output_dir", type=pathlib.Path)
    args = parser.parse_args()
    
    main()



# def make_slow_queries(q:str, fields:list) -> None:
#     for fOS in fields:
#         query_s2_by_field(q, fOS)
#         sleep(60*5)

# def raw2parquet(q:str, fOS:str) -> None:  
#     fnames = list(DIR.glob(f"output/s2search_data/{fOS}/{q}/*json"))
#     out = []
#     for fname in fnames:
#         print(fname)
#         with open(fname) as f:
#             d = json.load(f)
#             for line in d:
#                 out.append(line)
#     return pd.DataFrame(out).to_parquet(SPECTER_DIR / f"{q}-{fOS}.pqt")


# ------------------------ Testing digital humanities ------------------------ #

# Keyword search in API by year and field returns any paper from field (s2orc or mag) 
# containing a hit from the search algorithm. But on the website, I think they might fist
# consider the s2orc classification, then falls back on the mag_field if no s2 classif, 
# e.g. if s2field is not None s2field == 'Art' else is mag_field == 'Art' . 
# Considering only the s2field, we get from 28K hits for digital humanities in philosophy to
# 7819 hits. If we do the same query on the website (Digital humanities;1950-1921;Philosophy),
# we end up with  8,960 gits. We lost 1000 hits somehwere and we don't know why.  
# Still, 1000s missing hits is already better than 20K over.

# raw2parquet("digital humanities", "Philosophy")
# testDH = pd.read_parquet("s2search_data/digital humanities-Philosophy.pqt")

# testDH["s2Field"] = flatten_s2field(testDH)

# testDH_NoNull = testDH[~testDH["s2Field"].isnull()]
# testDH_NoNull = pd.DataFrame.explode(testDH_NoNull, "s2Field")\
#                             .query("s2Field == 'Philosophy'")\
#                             .drop_duplicates("paperId")

