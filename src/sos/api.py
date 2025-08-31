"""
Custom API for MongoDB to post, update, query, and delete MongoDB Science of Science Data
"""
from collections import Counter
import base64
from pymongo import UpdateOne
import time
from math import log10
import re
from typing import List, Any, Union, Dict, ClassVar
import io
import os
from pathlib import Path
import requests
import wget
from pymongo import MongoClient
import sys

import dotenv
dotenv.load_dotenv()

from tqdm import tqdm


from .db import DB

__all__ = [
    "CatException",
    "MissingSummary",
    "InvalidCatId",
]


class CatException(Exception):
    pass


class MissingSummary(CatException):
    pass


class InvalidCatId(CatException):
    pass

# cat_db = catDB()
# cat_db.augment_papers_with_s2orc_bool()


class sosDB:


    def __init__(self, client: MongoClient = None):
        if client is None:
            uri="mongodb://cwward:password@wranglerdb01a.uvm.edu:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
            client = MongoClient(uri)
        self.S2_API_KEY = os.environ['S2_API_KEY']
        self._db = DB(client)


    def already_exists(self, catalog) -> bool:
        """Check if a catalog already exists in the db."""
        collection = catalog.collection_name
        id = catalog.to_dict()['id']
        return self._db.find_one(id, collection) is not None


    ### Upload, Update, Find, Delete ###

    def import_s2orc(self):
        DATASET_NAME = "s2orc"
        LOCAL_PATH = Path("s2orc")
        LOCAL_PATH.mkdir(exist_ok=True)
        
        # get latest release's ID
        response = requests.get("https://api.semanticscholar.org/datasets/v1/release/latest").json()
        RELEASE_ID = response["release_id"]
        print(f"Latest release ID: {RELEASE_ID}")

        # get the download links for the s2orc dataset; needs to pass API key through `x-api-key` header
        # download via wget. this can take a while...
        response = requests.get(f"https://api.semanticscholar.org/datasets/v1/release/{RELEASE_ID}/dataset/{DATASET_NAME}/", headers={"x-api-key": S2_API_KEY}).json()
        for url in tqdm(response["files"]):
            match = re.match(r"https://ai2-s2ag.s3.amazonaws.com/staging/(.*)/s2orc/(.*).gz(.*)", url)
            assert match.group(1) == RELEASE_ID
            SHARD_ID = match.group(2)
            if SHARD_ID in ['20240510_111959_00105_cqrfv_06d4adea-44ca-4c46-acf8-2442f1defaab',
                            '20240510_111959_00105_cqrfv_1cba251d-aef5-43c8-982e-078aba5dfcfb',
                            '20240510_111959_00105_cqrfv_26e8442e-6d4f-4c4e-98d8-1a4f122f88cc',
                            '20240510_111959_00105_cqrfv_28a35758-9c8d-4bc0-945d-e5f01c9fac0b',
                            '20240510_111959_00105_cqrfv_3307f646-2017-47b1-bae8-82430de58d39',
                            '20240510_111959_00105_cqrfv_3622a0e7-0efa-4be4-bb22-c9ece78f4916',
                            '20240510_111959_00105_cqrfv_398c611c-2d1f-4e56-ae86-5ace26e449e7',
                            '20240510_111959_00105_cqrfv_46ed588b-f493-4abf-80ee-b6208802f791',
                            '20240510_111959_00105_cqrfv_4e604ad0-b75b-4829-b66a-9afd200911df',
                            '20240510_111959_00105_cqrfv_50200898-9cff-4a7c-a805-3913e98f921d',
                            '20240510_111959_00105_cqrfv_55db370d-465e-4469-8128-7e41aac65ecc',
                            '20240510_111959_00105_cqrfv_67d8fc39-f67a-4488-903a-e2a232c369d6',
                            '20240510_111959_00105_cqrfv_77647deb-565a-4007-9bbc-4f746be02fd8',
                            '20240510_111959_00105_cqrfv_79c1f956-08ef-4003-b884-bf0e0921bdee',
                            '20240510_111959_00105_cqrfv_8a7a64bd-9ae9-4519-81f0-ed5fa1e21bac',
                            '20240510_111959_00105_cqrfv_a215f6b4-0414-4939-87d1-45c7ce0b9a15',
                            '20240510_111959_00105_cqrfv_b5510af8-4171-4f54-a253-43209b0d0b8b',
                            '20240510_111959_00105_cqrfv_bba71f23-6043-4c32-a07a-f450aa75e618',
                            '20240510_111959_00105_cqrfv_c0909be6-2fd1-43b3-8179-1cbd8fe724cc',
                            '20240510_111959_00105_cqrfv_bfa26a57-037a-4073-851b-fe8f98ab6aa5',
                            '20240510_111959_00105_cqrfv_d3227579-d76d-4736-84d6-aa0c09854103',
                            '20240510_111959_00105_cqrfv_f440e705-035d-4043-9e53-73fc87336793',
                            '20240510_111959_00105_cqrfv_fee02487-45da-40dc-bd96-1558c6d2b7d1',
                            '20240510_111959_00105_cqrfv_fc45a9fc-8cac-45b0-9341-3d96c904d193']:
                wget.download(url, out=os.path.join(LOCAL_PATH, f"{SHARD_ID}.gz"))
        
        print("Downloaded all shards.")


    def upload(self, catalog) -> str:
        """Add a catalog object, return the id_."""
        if not self.already_exists(catalog):
            id_ = self._db.create(catalog) # create fields at top-level of the DB 
            self._db.update(catalog) # update the rest in 'metadata'
            return id_
        else:
            # if already exists, update it anyway
            self._db.update(catalog)

    def update(self, id: str, metadata: dict, collection: str ) -> str:
        """Update a catalog object."""
        self._db.update(id, metadata, collection)

    def find_one(self, id:str, agg_field: str, collection: str):
        """Add a catalog, return the id of catalog (id)."""
        db_item = self._db.find_one(id=id, agg_field=agg_field, collection=collection)
        if db_item is not None:
            db_item.pop('_id')
            return db_item
        else:
            raise InvalidCatId(id)
    
    def find_one_gridfs(self, id: str, collection: str, save_loc: bool = False):
        """Loads a file from a GridFS collection"""
        assert collection in ['cc_pdf', 'cc_png']
        try:
            db_item = self._db.find_one_gridfs(id, collection, save_loc=save_loc)
            if db_item is not None:
                return db_item
            else:
                raise InvalidCatId(id)
        except Exception as e:
            print(e)

    def find(self, id: str, agg_field: str, collection: str):
        """Add a catalog, return the id of catalog (id)."""
        db_items = self._db.find(id, agg_field, collection)
        if db_items is not None:
            out = []
            for item in db_items:
                item.pop('_id')
                out.append(item)
            return out
        else:
            raise InvalidCatId(id)
    
    def find_gridfs(self, id: str, agg_field: str, collection: str):
        """Add a catalog, return the id of catalog (id)."""
        try:
            return self._db.find_gridfs(id, agg_field, collection)
        except:
            raise InvalidCatId(id)

    def delete_one(self, id: str, collection: str) -> None:
        """Remove a catalog from db with given pdf_id."""
        try:
            self._db.delete_one(id, collection)
        except KeyError as exc:
            raise InvalidCatId(id) from exc

    def delete_all(self, id: str, agg_field: str, collection: str) -> None:
        """Remove a catalog from db with given pdf_id."""
        try:
            self._db.delete_all(id, agg_field, collection)    
        except KeyError as exc:
            raise InvalidCatId(id) from exc

    # !TODO: UPDATE ONE SHOULD BE IN db.py
    def augment_papers_with_s2orc_bool(self):
        """You need at least 30Gb of memory to run that"""
        for year in range(1960, 2023):
            print(f"Doing: {year}")

            start_time = time.time()
            self._db._db.papers.bulk_write(
                [
                    UpdateOne(
                        {"corpusid": doc["corpusid"]}, {"$set": {"s2orc_parsed": True}}
                    )
                    for doc in list(self._db._db.s2orc.find({}, {"corpusid": 1}))
                ]
            )
            print("Finished writing DOIs --- %s seconds ---" % (time.time() - start_time))

    def convert_mag_to_sting(self):
        """openAlex and s2orc don't have the same type for mag. We decided to convert OA mag into string."""
        # estimate time
        tot_documents = self._db.works_oa.estimated_document_count()
        works_oa_test_count = self._db.works_oa_test.estimated_document_count()
        start_time = time.time()
        self._db.works_oa_test.update_many({}, [ { "$addFields": { "mag": { "$toString": "$ids.mag" } } } ])
        test_time = (time.time() - start_time)   
        
        print(f"It took {round(test_time, 2)}s for {works_oa_test_count} documents")
        print(f"It should take {round(test_time * (10 ** log10((tot_documents / works_oa_test_count))) / 60, 2)} mins.")

        start_time = time.time()
        self._db.works_oa.update_many({}, [ { "$addFields": { "mag": { "$toString": "$ids.mag" } } } ])
        time_taken = (time.time() - start_time)
        print(f"Process finished {time_taken / 60} mins")
    

    def add_http(self):
        self.estimate_time()
        start_time = time.time()
        self._db.papers.update_many({}, [ 
            { "$set": { "doi": { "$cond": [ 
                { "$ne": ["$externalids.DOI", None] },
                { "$concat": ["https://doi.org/", "$externalids.DOI"] },
                None ] } 
            }}
        ])
        time_taken = (time.time() - start_time)
        print(f"Process finished {time_taken / 60} mins")


    def augment_papers_with_works_oa(self):
        """
        Augment openAlex on s2orc based on DOIs, without consideration for mag.
        The last few years you need more than 16Gb of memory to run it.
        Perhaps we could have done that faster without uploading openAlex on the DB first.
        We are basically loading in memory the papers for a given year and matching them
        to the relevant identifier in the `papers` collection.
        """
        year = int(sys.argv[1])
        print(f"Doing: {year}")
        start_time = time.time()
        self._db.papers.bulk_write(
            [
                UpdateOne(
                    {"doi": doc["doi"]}, {"$set": {"works_oa": doc["works_oa"][0]}}
                )
                for doc in self.doi_first(year)
            ]
        )
        print("Finished writing DOIs --- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        self._db.papers.bulk_write(
            [
                UpdateOne(
                    {"externalids.MAG": doc["externalids"]["MAG"]},
                    {"$set": {"works_oa": doc["works_oa"][0]}},
                )
                for doc in self.do_mag_with_no_doi(year)
            ]
        )
        print("Finished writing mag --- %s seconds ---" % (time.time() - start_time))

    #### UTILITIES ####


    def count(self, 
        x: str = None, 
        by: Union[str, List[str]] = None, 
        collection: str = None,
        match: Dict[str, Any] = None
    ) -> Union[int, Dict]:
        """Return the number [ror | pdf_idf] in a collection of the db."""
        return self._db.count(x=x, by=by, collection=collection, match=match)
    

    def estimate_time(self):
        tot_documents = self._db.papers.estimated_document_count()
        papers_test_count = self._db.papers_test.estimated_document_count()
        
        start_time = time.time()
        self._db.papers_test.update_many({}, [ 
            { "$set": { "doi": { "$cond": [ 
                { "$ne": ["$externalids.DOI", None] },
                { "$concat": ["https://doi.org/", "$externalids.DOI"] },
                None ] } 
            }}
        ])
        test_time = (time.time() - start_time)
        
        print(f"It took {round(test_time, 2)}s for {papers_test_count} documents")
        print(f"It should take {round(test_time * (10 ** log10((tot_documents / papers_test_count))) / 60, 2)} mins.")

    def do_arxiv(self, year):
        only_keep_existing_matches = {"$match": {"matches": {"$ne": []}}}

        s2orc_filter = {
            "$match": {
                "year": year,
                "externalids.arxiv": {"$type": "string"},
                "externalids.MAG": {"$type": None},
                "doi": {"$type": None},
            }
        }

        oa_filter_pipeline = {
            "$match": {
                "publication_year": year,
                "$expr": {"$eq": ["$$s2orc_arxiv", "$ids.arxiv"]},
            }
        }

        works_s2orc2oa_lookup_concise = {
            "$lookup": {
                "from": "works_oa",
                "localField": "externalids.MAG",
                "foreignField": "mag",
                "let": {"s2orc_mag": "$externalids.MAG"},
                "pipeline": [oa_filter_pipeline],
                "as": "matches",
            }
        }

        return list(
            self._db.papers.aggregate(
                [
                    s2orc_filter,
                    works_s2orc2oa_lookup_concise,
                    only_keep_existing_matches,
                    {
                        "$addFields": {
                            "works_oa": {
                                "$cond": [{"$ne": ["$matches", []]}, "$matches", None]
                            }
                        }
                    },
                    {"$project": {"matches": 0}},
                ]
            )
        )
    
    def doi_first(self, year):
        only_keep_existing_matches = {"$match": {"matches": {"$ne": []}}}

        s2orc_filter = {
            "$match": {
                "year": year,
                "doi": {"$type": "string"},
            }
        }

        oa_filter_pipeline = {
            "$match": {
                "publication_year": year,
                "$expr": {"$eq": ["$$s2orc_doi", "$doi"]},
            }
        }

        works_s2orc2oa_lookup_concise = {
            "$lookup": {
                "from": "works_oa",
                "localField": "doi",
                "foreignField": "doi",
                "let": {"s2orc_doi": "$doi"},
                "pipeline": [oa_filter_pipeline],
                "as": "matches",
            }
        }

        return list(
            self._db.papers.aggregate(
                [
                    s2orc_filter,
                    works_s2orc2oa_lookup_concise,
                    only_keep_existing_matches,
                    {
                        "$addFields": {
                            "works_oa": {
                                "$cond": [{"$ne": ["$matches", []]}, "$matches", None]
                            }
                        }
                    },
                    {"$project": {"matches": 0}},
                ]
            )
        )

    def do_mag_with_no_doi(self, year):
        only_keep_existing_matches = {"$match": {"matches": {"$ne": []}}}

        s2orc_filter = {
            "$match": {
                "year": year,
                "externalids.MAG": {"$type": "string"},
                "doi": {"$type": "null"},
            }
        }

        oa_filter_pipeline = {
            "$match": {
                "publication_year": year,
                "$expr": {"$eq": ["$$s2orc_mag", "$mag"]},
            }
        }

        works_s2orc2oa_lookup_concise = {
            "$lookup": {
                "from": "works_oa",
                "localField": "externalids.MAG",
                "foreignField": "mag",
                "let": {"s2orc_mag": "$externalids.MAG"},
                "pipeline": [oa_filter_pipeline],
                "as": "matches",
            }
        }

        return list(
            self._db.papers.aggregate(
                [
                    s2orc_filter,
                    works_s2orc2oa_lookup_concise,
                    only_keep_existing_matches,
                    {
                        "$addFields": {
                            "works_oa": {
                                "$cond": [{"$ne": ["$matches", []]}, "$matches", None]
                            }
                        }
                    },
                    {"$project": {"matches": 0}},
                ]
            )
        )
    
