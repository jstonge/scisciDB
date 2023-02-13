"""
How to update pymongo
"""

import json
from pathlib import Path

import numpy as np
from pymongo import ASCENDING
from tqdm import tqdm

from helpers import client


def create_indexes(db, yr1, yr2):
    print(f"Doing {yr1}-{yr2}")
    index_db = [_ for _ in db.metadata.index_information()]
    name_index = f"bucket {yr1}-{yr2}"
    if name_index not in index_db:
        PFE = { "year" : { "$gte": yr1, "$lte": yr2 }, "abstract": {"$type": "string"} }
        db.metadata.create_index(
            [("year", ASCENDING)], 
            name=name_index, 
            partialFilterExpression=PFE
            )

if __name__ == "__main__":
    
    ROOT_DIR = Path()
    LOOKUP_DIR = ROOT_DIR / 's2FOS_lookup'
    
    all_lookups = np.array(list(LOOKUP_DIR.glob("*json")))
    
    yr = [int(str(l).split("/")[-1].split("_")[1]) for l in all_lookups]
    lookups_sorted = all_lookups[np.argsort(yr)]
    
    db = client["papersDB"]

    # index by decade b/c fewer papers
    for yr1, yr2 in tqdm(zip(range(1950, 1990, 10), range(1960, 2000, 10))):
        # db.metadata.drop_index(f"bucket {yr1}-{yr2}")
        create_indexes(db, yr1, yr2)
    
    # index by half-decade b/c more papers. We might even want to split further.
    for yr1, yr2 in tqdm(zip(range(1990, 2020, 5), range(1995, 2025, 5))):
        # db.metadata.drop_index(f"bucket {yr1}-{yr2}")
        create_indexes(db, yr1, yr2)


    for i in range(0, len(lookups_sorted)-1):
        
        with open(ROOT_DIR / lookups_sorted[i]) as f:
            d = json.load(f)
        
        yr1 = int(str(lookups_sorted[0]).split("/")[-1].split("_")[1])
        yr2 = int(str(lookups_sorted[0+1]).split("/")[-1].split("_")[1])

        for pid, fos in tqdm(d.items()):
            q = {"paper_id": pid, "year": { "$gte": yr1, "$lte": yr2 }, "abstract": {"$type": "string"}}
            new_values = {"$set": { "s2fos_field_of_study": fos} }
            db.metadata.update_one(q, new_values)

    
    
    

    


    paper_id = "84881204"
    field = "medicine"
    # decade = 1960

    
