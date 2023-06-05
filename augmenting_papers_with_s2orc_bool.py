import time
from pymongo import UpdateOne
from creds import client

db = client["papersDB"]

def main():
    """You need at least 30Gb of memory to run that"""
    for year in range(1960, 2023):
        print(f"Doing: {year}")

        start_time = time.time()
        db.papers.bulk_write(
            [
                UpdateOne(
                    {"corpusid": doc["corpusid"]}, {"$set": {"s2orc_parsed": True}}
                )
                for doc in list(db.s2orc.find({}, {"corpusid": 1}))
            ]
        )
        print("Finished writing DOIs --- %s seconds ---" % (time.time() - start_time))
    
if __name__ == "__main__":
    main()