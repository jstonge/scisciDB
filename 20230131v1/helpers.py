
from faker import Faker

import pandas as pd
from tqdm import tqdm
from pymongo import MongoClient

from multiprocessing import cpu_count

pw = "password"

uri = f"mongodb://cwward:{pw}@wranglerdb01a.uvm.edu:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
client = MongoClient(uri)

num_cores = cpu_count() - 1
fake = Faker()

def create_dataframe(arg):
    x = int(6000/num_cores)
    data = pd.DataFrame()
    for i in tqdm(range(x), desc='Creating DataFrame'):
        data.loc[i, 'first_name'] = fake.first_name()
        data.loc[i, 'last_name'] = fake.last_name()
        data.loc[i, 'job'] = fake.job()
        data.loc[i, 'company'] = fake.company()
        data.loc[i, 'address'] = fake.address()
        data.loc[i, 'city'] = fake.city()
        data.loc[i, 'country'] = fake.country()
        data.loc[i, 'email'] = fake.email()
    return data
