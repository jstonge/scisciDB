"""
Update mongoDB or openalex
"""
import argparse
from jsonlines import jsonlines
import json
from pathlib import Path
# from creds import client
from tqdm import tqdm
import re
import pickle
import gzip

import dotenv
dotenv.load_dotenv()

from pymongo import MongoClient

def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-i",
        "--input",
        type= Path,
        help="JSONlines file with urls and hashes",
        required=True,
    )
    parser.add_argument(
        "-c", "--collection", type=str, help="MongoDB collections", required=True
    )
    return parser.parse_args()

def read_cache(file):
    if file.exists():
        with open(file, 'rb') as f:
            dat = pickle.load(f)
    else:
        file.touch()
        dat = []
    return set(dat)

def update_cache(file, dat, done_ids):
    new_ids = set([hash(x['id']) for x in dat])
    done_ids = done_ids | new_ids
    print(f"We now have {len(done_ids)} documents done.")
    with open(file, 'ab') as f:
        pickle.dump(done_ids, f)

def main():
    pw = "password"
    uri = f"mongodb://cwward:{pw}@wranglerdb01a.uvm.edu:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
    client = MongoClient(uri)

    args = parse_args()
    # INPUT_DIR=Path("data/openalex-snapshot/data/works")
    # INPUT_DIR=Path("data/s2-papers")
    # COLLECTION='s2-papers'
    
    INPUT_DIR = args.input 
    COLLECTION = args.collection

    cache_file = Path(".cache") / f"{COLLECTION}.pkl"
     
    db = client["papersDB"]
    
    if db[COLLECTION].find_one() is None and cache_file.exists(): 
        cache_file.unlink()
    
    done_ids = read_cache(cache_file)
    
    # openalex stores is data as a list of DIRS
    for file in list(INPUT_DIR.rglob("*")):
        # break
        dat = []
        if str(file).endswith("gz"):
            with gzip.open(file, 'rt', encoding='utf-8') as f:
                for line in tqdm(f):
                    obj=json.loads(line)
                    if obj['id'] not in done_ids:
                        dat.append(obj)
            
    
        else:
            with jsonlines.open(file) as f:
                for obj in tqdm(f):
                    dat.append(obj)
    
    db[COLLECTION].insert_many(dat)
        
    update_cache(cache_file, dat, done_ids)

if __name__ == "__main__":
    
    main()



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