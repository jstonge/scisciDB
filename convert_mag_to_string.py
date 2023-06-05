import time
from math import log10
from creds import client

db = client['papersDB']

def estimate_time():
    tot_documents = db.works_oa.estimated_document_count()
    works_oa_test_count = db.works_oa_test.estimated_document_count()
    start_time = time.time()
    db.works_oa_test.update_many({}, [ { "$addFields": { "mag": { "$toString": "$ids.mag" } } } ])
    test_time = (time.time() - start_time)   
    print(f"It took {round(test_time, 2)}s for {works_oa_test_count} documents")
    print(f"It should take {round(test_time * (10 ** log10((tot_documents / works_oa_test_count))) / 60, 2)} mins.")

def main():
    """openAlex and s2orc don't have the same type for mag. We decided to convert OA mag into string."""
    estimate_time()
    start_time = time.time()
    db.works_oa.update_many({}, [ { "$addFields": { "mag": { "$toString": "$ids.mag" } } } ])
    time_taken = (time.time() - start_time)
    print(f"Process finished {time_taken / 60} mins")

main()