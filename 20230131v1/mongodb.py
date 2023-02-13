"""
How to generate fake data on pymongo
see: https://www.percona.com/blog/how-to-generate-test-data-for-mongodb-with-python/
"""

from multiprocessing import Pool, cpu_count

import pandas as pd

from helpers import client, create_dataframe

if __name__ == "__main__":
    num_cores = cpu_count() - 1
    with Pool() as pool:
        data = pd.concat(pool.map(create_dataframe, range(num_cores)))

    data_dict = data.to_dict('records')
    db = client["papersDB"]
    collection = db["employees"]
    collection.insert_many(data_dict)
