"""
Update mongoDB or openalex
"""
import argparse
from jsonlines import jsonlines
from pathlib import Path
from creds import client
from tqdm import tqdm
import pickle

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
    db = client["papersDB"]
    
    if db[args.corpus+'_oa'].find_one() is None and cache_file.exists(): 
        cache_file.unlink()
    
    done_ids = read_cache(cache_file)

    if args.source == 's2':
        # semantic scholars stores is data as a list of files.
        # File size will depend on its content, e.g.
        # authors are ~700Mb while papers ~6.3Gb.
        # Meaning that we should ask for more or less memory 
        # dependending on the collection.
        files = list(CORPUS_DIR.glob("20230203_*"))
        for i, file in enumerate(files):
            if str(file).endswith("gz") == False:
                print(f"{i} / {len(files)}")
                dat = []
                with jsonlines.open(file) as f:
                    for obj in tqdm(f):
                        dat.append(obj)
        db[args.corpus].insert_many(dat)
    
    else:
        # openalex stores is data as a list of DIR
        folders = list(CORPUS_DIR.glob("updated_date*"))
        for i,folder in enumerate(folders):

            print(f"{i} / {len(folders)}")
            # ...each having one or multiple files. 
            files = list(folder.glob("*"))
            
            for i, file in enumerate(files):
                print(f"{i} / {len(files)}")
                data = []
                with jsonlines.open(file) as f:
                    for obj in tqdm(f):
                        if obj['id'] not in done_ids:
                            data.append(obj)
                
                db[args.corpus+'_'+args.source].insert_many(data)
            
            update_cache(cache_file, data, done_ids)

if __name__ == "__main__":
    # source, corpus = 'oa', 'works'
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help="s2 (semantic scholar) or oa (openalex)")
    parser.add_argument("-c", "--corpus", help="corpus within data source")
    args = parser.parse_args()

    assert args.source in ['oa', 's2'], "Data source doesn't exists. We have `s2` or `oa`"   

    ROOT_DIR = Path()
    SOURCE_DIR = ROOT_DIR / '20230131v1' if args.source == 's2' else ROOT_DIR / 'openalex-snapshot'
    CORPUS_DIR = SOURCE_DIR / 'data' / args.corpus
    CACHE_DIR = Path(".cache")

    cache_file = CACHE_DIR / f"{args.corpus}_{args.source}.pkl"
     
    assert CORPUS_DIR.exists(), "Corpus folder doesn't exist. Maybe you are in the wrong directory?" 

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