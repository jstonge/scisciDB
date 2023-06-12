# scisciDB

A database to do science of science.

![image](https://user-images.githubusercontent.com/35715881/218609701-96d465da-888a-4698-a7b2-53a840c53218.png)

|              | works  | citations | authors | venues | institutions | text_parsed | embeddings
| -------------| ------------- | ------------- | ------------- |------------- |------------- |------------- |------------- |
| semantic scholar|  210M | 2.4B | 80.4M   | 191.5K | ? | 10.2M | 120M

## Instructions

 - `update_mongodb.sh`: push and pull data from and to the papersDB collection in our mongoDB. Run 

```shell
# update authors from openalex
sh update_mongodb.sh oa authors
```
