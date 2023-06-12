import time
from pymongo import UpdateOne
from creds import client
import sys

db = client["papersDB"]

def doi_first(year):
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
        db.papers.aggregate(
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

def do_mag_with_no_doi(year):
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
        db.papers.aggregate(
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

def do_arxiv(year):
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
        db.papers.aggregate(
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

def main():
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
    db.papers.bulk_write(
        [
            UpdateOne(
                {"doi": doc["doi"]}, {"$set": {"works_oa": doc["works_oa"][0]}}
            )
            for doc in doi_first(year)
        ]
    )
    print("Finished writing DOIs --- %s seconds ---" % (time.time() - start_time))

    start_time = time.time()
    db.papers.bulk_write(
        [
            UpdateOne(
                {"externalids.MAG": doc["externalids"]["MAG"]},
                {"$set": {"works_oa": doc["works_oa"][0]}},
            )
            for doc in do_mag_with_no_doi(year)
        ]
    )
    print("Finished writing mag --- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
