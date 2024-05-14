"""
DB for the cat-project
"""
from pymongo import MongoClient
from gridfs import GridFS
import traceback
from typing import List, Union, Dict, Any

class DB:
    def __init__(self, client: MongoClient):
        self.client = client
        self._db = self.client['papersDB']

    def create(self, catalog) -> int:
        """
        Different collections for different types of data (GridFS > 16MB files).
        Collection Names are hardcoded.
        """
        collection = catalog.collection_name
        item = catalog.to_dict()
        if collection in ['cc_pdf', 'cc_png']:
            fs = GridFS(self._db, collection=collection)
            id = fs.put(item['file'], id=item['id'])
        else:
            dat_dict = {'id': item['id'] }
            if item.get('text'):
                dat_dict.update({'text': item['text']})
            id = self._db[collection].insert_one(dat_dict)
        return id
    
    def update(self, catalog) -> None:
        """
        Update metadata with some changes.
        It won't update the fields that are already there.
        """
        collection = catalog.collection_name
        mods = { 'metadata': catalog.to_dict() }
        id = catalog.to_dict()['id']
        # Ensure collection name adjustment for GridFS metadata updates
        collection_name = f'{collection}.files' if collection in ['cc_pdf', 'cc_png'] else collection
        # Get the collection and metadata
        catalog = self._db[collection_name].find_one({"id": id})
        
        # We assume that we update one key at a time, e.g. 'metadata', 'tokens', or top-level.
        assert len(mods.keys()) == 1, "Upload one key at at time"
        (key,), (changes,) = zip(*mods.items())

        changes = {k: v for k, v in changes.items() if k not in ['id', 'text', 'file']}

        catalog_metadata = catalog.get(key, {})
        catalog_metadata.update(changes)
        
        # Update the metadata with the changes
        self._db[collection_name].update_one(
            { "id": id }, 
            {"$set": { key: catalog_metadata }}
            )
        
    def find_one(self, id: str, collection: str, agg_field: str = None):
        collection_name = f'{collection}.files' if collection in ['cc_pdf', 'cc_png'] else collection
        if agg_field is None:
            query = {"id": id}
        else:
            query = {f"metadata.{agg_field}": id}
        item = self._db[collection_name].find_one(query)
        return item
    
    def find(self, id: str, agg_field: str, collection: str):
        collection_name = f'{collection}.files' if collection in ['cc_pdf', 'cc_png'] else collection
        return list(self._db[collection_name].find({f"metadata.{agg_field}": id}))

    def find_one_gridfs(self, id: str, collection:str, save_loc:bool = False):
        fs = GridFS(self._db, collection=collection)
        try:
            obj = fs.find_one({"id": id})
            if obj is not None:
                if save_loc:
                    with open(f"{id}.{collection.split('_')[-1]}", 'wb') as file:
                        file.write(fs.get(obj._id).read())
                    print(f"Downloaded {id} at {save_loc}")
                else:
                    return fs.get(obj._id).read()
        except Exception as e:
                print(f"Failed to load {id}")
                print("Error:", e)
                traceback.print_exc()
    
    def find_gridfs(self, id: str, agg_field: str, collection: str, save_loc: bool = False):
        fs = GridFS(self._db, collection=collection)
        try:
            if save_loc:
                pass
            else:
                out = []
                for grid_out in fs.find({f"metadata.{agg_field}": id}):
                    out.append(grid_out.read())
                return out
        except Exception as e:
                print(f"Failed to load {id}")
                print("Error:", e)
                traceback.print_exc()

    def delete_one(self, id: str, collection: str) -> None:
        self._db[collection].delete_one({"id": id})
    
    def delete_all(self, id: str, agg_field: str, collection: str) -> None:
        if collection in ['cc_pdf', 'cc_png']:
            fs = GridFS(self._db, collection=collection)
            if agg_field in ['inst_id', 'pdf_id']:
                inst_fs = list(fs.find({f"metadata.{agg_field}": id}))
                [fs.delete(obj._id) for obj in inst_fs]
        else:
            d = self._db[collection].delete_many({f"metadata.{agg_field}": id})
            print(d.deleted_count, " documents deleted !!")
        
        print(f"Deleted {id} from {collection}")

    def count(self, x: str = None, by: Union[str, List[str]] = None, collection: str = None, match: Dict[str, Any] = None) -> Union[int, Dict]:
        """
        Count documents in a collection, optionally filtered by criteria and/or ID,
        and grouped by specified fields.

        :param x: (Optional) Specific ID for filtering with a single aggregation field.
        :param by: (Optional) Field(s) to aggregate by.
        :param collection: Name of the collection to aggregate.
        :param match: (Optional) Dictionary of criteria to filter documents.
        :return: Count of documents, or a dictionary of counts if grouped by fields.

        EXAMPLE
        =======
        ```python
        cat_db.count("0155zta11", by="inst_id", collection="cc_catalog")
        ```
        """
        if collection is None:
            raise ValueError("Parameter 'collection' must be provided")
        
        # Adjust collection name for special cases (e.g., GridFS collections)
        collection_name = f'{collection}.files' if collection in ['cc_pdf', 'cc_png'] else collection

        # Normalize 'by' parameter to a list for consistency
        if isinstance(by, str):
            by = [by]

       # Ensure 'by' fields are valid, assuming all fields within 'metadata' are considered valid
        valid_fields = ['inst_id', 'pdf_id', 'conversion']
        if by and not all(field in valid_fields for field in by):
            raise ValueError(f"Invalid aggregation field(s). Valid options: {valid_fields}")

        # Construct initial match criteria from 'match' parameter and optional 'x' parameter
        match_stage = match if match else {}
        if x and by and len(by) == 1:
            match_stage[f"metadata.{by[0]}"] = x  # Adjusting for nested structure
        
        # Build aggregation pipeline starting with match stage if criteria exist
        pipeline = [{'$match': match_stage}] if match_stage else []

        # Add group stage to pipeline if 'by' parameter is specified for aggregation
        if by:
            # Ensure correct path for the field, especially for nested fields within 'metadata'
            group_field = f"$metadata.{by[0]}" if collection in ['cc_pdf', 'cc_png'] else f"$metadata.{by[0]}"
            pipeline.append({'$group': {'_id': group_field, 'count': {'$sum': 1}}})

        # Execute aggregation pipeline
        results = list(self._db[collection_name].aggregate(pipeline))

        # Process and return results based on aggregation type (grouped or ungrouped)
        if not by or len(by) == 1 and x:
            # Return total count for ungrouped query
            return sum(res['count'] for res in results) if results else 0
        else:
            # Return dictionary of counts for grouped results
            return {(tuple(res['_id'].values()) if isinstance(res['_id'], dict) else res['_id']): res['count'] for res in results}