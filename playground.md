# How to get started with mongoDB using `mongosh`. 

I currently use the vscode plug-in to interact with mongoDB. 
See https://code.visualstudio.com/docs/azure/mongodb.
I like it b/c it is a middle between mongoDB Compass and the commandline.

Key refs:

 - `install mongosh:` https://www.mongodb.com/docs/mongodb-shell/install/
 - `data modeling:` https://www.mongodb.com/docs/manual/core/data-modeling-introduction/
 - `operators`: https://www.mongodb.com/docs/manual/reference/operator/query/
 - `Monitoring DB`: https://www.percona.com/blog/monitoring-mongodb-collection-stats-with-percona-monitoring-and-management/
 - `Update documents`: https://www.mongodb.com/docs/mongodb-shell/crud/update/
 - `Queries`:
    - https://www.mongodb.com/docs/manual/tutorial/query-array-of-documents/
 - `indexes`: 
    - https://www.mongodb.com/basics/mongodb-index
    - https://www.mongodb.com/docs/manual/indexes/
    - https://www.percona.com/blog/2018/09/04/mongodb-index-usage-and-mongodb-explain-part-1/
    - https://www.percona.com/blog/2018/09/06/mongodb-investigate-queries-with-explain-index-usage-part-2/
    - https://www.bmc.com/blogs/mongodb-indexes/
 - `best practices:`
    - https://www.mongodb.com/basics/best-practices


Connect to papersDB
```shell
[direct: mongos] test> use('papersDB');
```
```python
from pymongo import MongoClient
uri = f"mongodb://cwward:{pw}@wranglerdb01a.uvm.edu:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
client = MongoClient(uri)
db = client["papersDB"]
```

Looking at collections within our DB
```shell
[direct: mongos] test> show collections;
```

Look at already existing indexes
```shell
[direct: mongos] papersDB> db.metadata.getIndexes()
```

estimate count document based on year is super quick
```shell
[direct: mongos] papersDB> db.metadata.estimatedDocumentCount()
```

you can 'explain' queries. Super useful to understand how mongoDB works and query performances.

```shell
[direct: mongos] papersDB> var exp = db.metadata.explain("executionStats")
[direct: mongos] papersDB> exp.find({title: "Scale-free networks are rare"}) // executionTimeMillis: 14827; totalDocsExamined: 19,786,006
[direct: mongos] papersDB> db.metadata.createIndex({year: -1}); // create index based on age
[direct: mongos] papersDB> exp.find({title: "Scale-free networks are rare", year: 2018}).limit(1) // executionTimeMillis: 3851; totalKeysExamined: 786,497
```

dropping indexes

```shell
[direct: mongos] papersDB> db.metadata.dropIndex("year_-1")
```

## USEFUL QUERIES


1-find papers based on `paper_id`

```shell
[direct: mongos] papersDB> db.pdf_parses.findOne({ paper_ID: "77497072"});
```

```python
db.metadata.find_one({ "paper_ID": "77497072"})
```

2-find papers based on `paper_id` and year
```shell
[direct: mongos] papersDB> db.metadata.findOne({ year: {$gt: 2015, $lt: 2022}, paper_id: "f1b4361a1978e93018c5fdfe4856250152676ffb" })
```

3-Query papers with `body_text`
see [stack overflow](https://stackoverflow.com/questions/14789684/find-mongodb-records-where-array-field-is-not-empty)

```shell
[direct: mongos] papersDB> db.pdf_parses.findOne({ body_text: { $gt: true, $type: 'array', $ne: [] }})
```

4-Query authors

```shell
[direct: mongos] papersDB> db.metadata.findOne({ 'authors.0.first': "Aaron" })
[direct: mongos] papersDB> db.metadata.findOne({ 'authors.first': "Aaron" })
[direct: mongos] papersDB> db.metadata.findOne({ 'authors.last': "Clauset" })
```

## CREATING INDEX 


Create index based on descending year
```shell
[direct: mongos] papersDB> db.metadata.createIndex({year: -1});
```
From Percona, this allows to improve all the queries that find documents with a condition and the year field, like the following:
```shell
[direct: mongos] papersDB> db.metadata.find( { year : 2018 } ) 
[direct: mongos] papersDB> db.metadata.find( { title : "Scale-free networks are rare", year : 2018 } )
[direct: mongos] papersDB> db.metadata.find( { year : { $gt : 2020} } )
[direct: mongos] papersDB> db.metadata.find().sort( { year: -1} ).limit(10)
```

Create index based on authors (Multikey indexes)

```shell
[direct: mongos] papersDB> db.metadata.createIndex( { authors: 1 } )
[direct: mongos] papersDB> db.metadata.find( { authors.last: "Clauset" } )
```

Create index based on year and `has_body_text` (include a Partial indexes and Unique)
In order for the partial index to be used the queries must contain a condition on the year and body_text field.

```shell
[direct: mongos] papersDB> db.metadata.createIndex(
   { "paper_id": 1 },
   { unique: true },
   { partialFilterExpression: { year : { $gt: 2018 }, body_text: { $gt: true, $type: 'array', $ne: [] } } }
)

[direct: mongos] papersDB> db.metadata.find( { paper_id: "77490322", year: { $gt: 2018}, body_text: { $gt: true, $type: 'array', $ne: []} } )
```

Create index based on year (asc) and bounded by 1950-60

```shell
[direct: mongos] papersDB> exp.find({"year": {$gte: 1950, $lte: 1960}, "paper_id": "77490322"}).limit(1) // executionTimeMillis: 360429; totalKeysExamined: 2024098
[direct: mongos] papersDB> db.metadata.createIndex({year:1}, { partialFilterExpression: { year : { $gte: 1950, $lte: 1960 } } });
[direct: mongos] papersDB> exp.find({"year": {$gte: 1950, $lte: 1960}, "paper_id": "77490322"}).limit(1) // executionTimeMillis: 68676; totalKeysExamined: 406162
```

Create index based partial filter expression

```python
# We use "$type" because "$ne" not supported when creating PFE
db.metadata.create_index(
 [("year", ASCENDING)], 
 name="bucket 1950-1960", 
 partialFilterExpression={ "year" : { "$gte": 1950, "$lte": 1960 }, "abstract": {"$type": "string"} }
)
```

## UPDATING DOCUMENTS 

1- Update s2fos 
```shell
db.metadata.updateOne({paper_id: '84881204', year: {$gte: 1950, $lte: 1960}}, {'$set': {'s2fos_field_of_study': ['Medicine']}}})
```

2- Remove a field
```shell
db.metadata.updateOne({paper_id: '84881204', year: {$gte: 1950, $lte: 1960}}, {$unset: {s2fos: ""}})
```

## SQL v. mongoDB SHOWDOWN

1-finding people

```shell
[direct: mongos] papersDB> db.metadata.aggregate({ $filter : { authors.last : { $eq : "Clauset" } } });
```

```sql
SELECT * FROM metadata
WHERE authors.last = "Clauset";
```

## USEFUL AGGREGATED QUERIES


Find duplicated rows (not sure it is working yet)

```shell
[direct: mongos] papersDB> const aggregation = [
    {"$group" : { "_id": "$paper_id", "count": { "$sum": 1 } } },
    {"$match": {"_id" :{ "$ne" : null } , "count" : {"$gt": 1} } }, 
    {"$project": {"paper_id" : "$_id", "_id" : 0} }
]

[direct: mongos] papersDB> db.pdf_parses.aggregate(aggregation);
```

## DOCUMENTS EMBEDDINGS


Embed one collection into a second collection 
not sure it is working yet, this is a chatgpt answer

```shell
[direct: mongos] papersDB> db.collection1.update({name: "John Doe"}, {$set: {address: db.collection2.findOne({address: "123 Main St"})}})
```

