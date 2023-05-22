import time
from pymongo import UpdateOne
from creds import client

db = client["papersDB"]

def doi_first(year):
    only_keep_existing_matches = {"$match": {"matches": {"$ne": []}}}

    s2orc_filter = {
        "$match": {
            "year": year,
            "s2fieldsofstudy.category": "Biology",
            "doi": {"$type": "string"},
        }
    }

    oa_filter_pipeline = {
        "$match": {
            "publication_year": year,
            "concepts.display_name": "Biology",
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
            "s2fieldsofstudy.category": "Biology",
            "externalids.MAG": {"$type": "string"},
            "doi": {"$type": "null"},
        }
    }

    oa_filter_pipeline = {
        "$match": {
            "publication_year": year,
            "concepts.display_name": "Biology",
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

def main():
    # Augment openAlex on s2orc based on DOIs, without consideration for mag
    for year in range(2004, 2023):
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
