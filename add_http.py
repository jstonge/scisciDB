import time
from math import log10
from creds import client

db = client['papersDB']

def estimate_time():
    tot_documents = db.papers.estimated_document_count()
    papers_test_count = db.papers_test.estimated_document_count()
    
    start_time = time.time()
    db.papers_test.update_many({}, [ 
        { "$set": { "doi": { "$cond": [ 
            { "$ne": ["$externalids.DOI", None] },
            { "$concat": ["https://doi.org/", "$externalids.DOI"] },
            None ] } 
        }}
    ])
    test_time = (time.time() - start_time)
    
    print(f"It took {round(test_time, 2)}s for {papers_test_count} documents")
    print(f"It should take {round(test_time * (10 ** log10((tot_documents / papers_test_count))) / 60, 2)} mins.")

def main():
    estimate_time()
    start_time = time.time()
    db.papers.update_many({}, [ 
        { "$set": { "doi": { "$cond": [ 
            { "$ne": ["$externalids.DOI", None] },
            { "$concat": ["https://doi.org/", "$externalids.DOI"] },
            None ] } 
        }}
    ])
    time_taken = (time.time() - start_time)
    print(f"Process finished {time_taken / 60} mins")

if __name__ == "__main__":
    main()