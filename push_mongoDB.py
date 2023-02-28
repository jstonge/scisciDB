"""
Update mongoDB or openalex
"""
import argparse
import gzip
from pathlib import Path
from typing import Dict, List

from jsonlines import jsonlines
from tqdm import tqdm

from creds import client


def read_jsonl_gz(filename) -> List[Dict]:
    data = []
    with gzip.open(filename, 'rb') as fp:
        j_reader = jsonlines.Reader(fp)

        for obj in j_reader:
            data.append(obj)

    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help="s2 (semantic scholar) or oa (openalex)")
    parser.add_argument("-c", "--corpus", help="corpus within data source")
    args = parser.parse_args()

    assert args.source in ['oa', 's2'], "Data source doesn't exists. We have `s2` or `oa`"
    
    ROOT_DIR = Path()
    # for now we hardcode the date
    SOURCE_DIR = ROOT_DIR / '20230131v1' if args.source == 's2' else ROOT_DIR / 'openalex-snapshot' / 'data'
    # SOURCE_DIR = ROOT_DIR / 'openalex-snapshot' / 'data'
    CORPUS_DIR = SOURCE_DIR / args.corpus
    print(f"Doing corpus {args.corpus} in {args.source}")
    assert CORPUS_DIR.exists(), "Corpus folder doesn't exist. Maybe you are in the wrong directory?"

    db = client["papersDB"]
    
    # corpus = 'authors'
    if args.source == 's2':
        files = list(CORPUS_DIR.glob("20230203_*"))
        for file in tqdm(files):
            if str(file).endswith("gz") == False:
                dat = []
                with jsonlines.open(file) as f:
                    for obj in f:
                        dat.append(obj)
        db[args.corpus].insert_many(dat)
    
    else:
        folders = list(CORPUS_DIR.glob("*"))
        for folder in tqdm(folders):
            for file in folder.glob("*gz"):
                dat = read_jsonl_gz(file)
                db[args.corpus+'_oa'].insert_many(dat)



# LOOKUP_DIR = ROOT_DIR / 's2FOS_lookup'
# all_lookups = np.array(list(LOOKUP_DIR.glob("*json")))
# yr = [int(str(l).split("/")[-1].split("_")[1]) for l in all_lookups]
# lookups_sorted = all_lookups[np.argsort(yr)]

# def create_indexes(db, yr1, yr2):
#     print(f"Doing {yr1}-{yr2}")
#     index_db = [_ for _ in db.metadata.index_information()]
#     name_index = f"bucket {yr1}-{yr2}"
#     if name_index not in index_db:
#         PFE = { "year" : { "$gte": yr1, "$lte": yr2 }, "abstract": {"$type": "string"} }
#         db.metadata.create_index(
#             [("year", ASCENDING)], 
#             name=name_index, 
#             partialFilterExpression=PFE
            # )


# # index by decade b/c fewer papers
# for yr1, yr2 in tqdm(zip(range(1950, 1990, 10), range(1960, 2000, 10))):
#     # db.metadata.drop_index(f"bucket {yr1}-{yr2}")
#     create_indexes(db, yr1, yr2)

# # index by half-decade b/c more papers. We might even want to split further.
# for yr1, yr2 in tqdm(zip(range(1990, 2020, 5), range(1995, 2025, 5))):
#     # db.metadata.drop_index(f"bucket {yr1}-{yr2}")
#     create_indexes(db, yr1, yr2)
# for i in range(0, len(lookups_sorted)-1):
    
#     with open(ROOT_DIR / lookups_sorted[i]) as f:
#         d = json.load(f)
    
#     yr1 = int(str(lookups_sorted[0]).split("/")[-1].split("_")[1])
#     yr2 = int(str(lookups_sorted[0+1]).split("/")[-1].split("_")[1])
#     for pid, fos in tqdm(d.items()):
#         q = {"paper_id": pid, "year": { "$gte": yr1, "$lte": yr2 }, "abstract": {"$type": "string"}}
#         new_values = {"$set": { "s2fos_field_of_study": fos} }
#         db.metadata.update_one(q, new_values)
