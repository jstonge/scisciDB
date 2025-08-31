
## SOS cli

### Installation

Install the `scisciDB` command line interface, called `sos`, using the following command:

```zsh
pip install ./scisciDB
```

Since it calls the mongoDB without authentification, you need to be on the `UVM` server for the CLI to work.

## Why?

We want to have full text of scientific works. The only way to do it at the moment is to upload `s2orc`. We want `s2orc` to be enriched with `openAlex` metadata. So we build that small library to facilitate the interoperability of `s2orc` and `openAlex`.

The library takes care of importing and keeping the DBs up to date on our MongoDB, as well as enriching one with the other when necessary, in a way that is practical. It integrates with the VACC.

### Higlights

A database to do science of science.

![image](https://user-images.githubusercontent.com/35715881/218609701-96d465da-888a-4698-a7b2-53a840c53218.png)

|              | works  | citations | authors | venues | institutions | text_parsed | embeddings
| -------------| ------------- | ------------- | ------------- |------------- |------------- |------------- |------------- |
| semantic scholar|  210M | 2.4B | 80.4M   | 191.5K | ? | 10.2M | 120M

## TODO

- [ ] upload s2orc from last snapshot
- [ ] upload openAlex from last snapshot
- [ ] upload s2orc last snapshot with openAlex last snapshot
- [ ] sample DBs in way that cannot easily be done with their APIs
  - [ ] sample parsed papers based on FoS.

## Accessing the mongoDB

#### Using MongoDB Compass
 - Download [MongoDB Compass](https://www.mongodb.com/products/tools/compass)
 - Follow these [instructions](https://www.uvm.edu/it/kb/article/sslvpn2/) to get on UVM's VPN.
 - Ask me to send you the credentials.


## Updating the DB

We are in the process of updating the DB to make it easier to keep it synchronize with OpenAlex and S2ORC.

#### SOS CLI:

 - [ ] ready to use
   - [x] backbone is created (api.py, db.py, cli.py)
   - [ ] integrating `import` functions into the api (e.g. `s2_import.py`, `oa_import.sh`)
   - [ ] integrating `sync` functions into the api
   - [ ] integrating `push_db` functions into the api (e.g. `oa_push_db.py`, `s2_push_db.py`)
   - [ ] integrating `pull_db` functions into the api (e.g. `pull_data.py`)
   - [ ] integrating function to facilitate DBs interoperability:
    - [ ] integrating `augmenting_papers_with_works_oa.py` function into the api
   - [ ] writing tests

#### OpenAlex collections

One of the main changes with openAlex that they made concepts obsolete in favor of topics.

 - [x] authors
 - [ ] concepts
 - [ ] domains
 - [ ] fields
 - [ ] funders
 - [x] institutions
 - [ ] merged_ids
 - [x] publishers
 - [x] sources
 - [ ] subfields
 - [x] topics
 - [ ] works (in process)
 
#### Semantic scholar collections

We can now directly update s2orc from their API (instead of bulk download). They made it so that we can sync the differences between snapshots.

 - [x] s2orc
 - [ ] abstract
 - [ ] citations?
 - [ ] papers
 - [ ] paper-ids
 - [ ] publication-venues
 - [ ] tldrs
