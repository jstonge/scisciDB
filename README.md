# s2orc

This repo is for keeping track of simple data wrangling with the [allenai's s2orc](https://github.com/allenai/s2orc) database.

see [project status](https://github.com/users/jstonge/projects/9).

#### Workflow

We are using an `ansible-playbook` to provide guidance on our data pipeline. To run specific part of the workflow, use tags in the playbook from the command line, e.g.

```zsh
ansible-playbook playbook.yaml --tags augment_s2orc_with_s2fos
```
To see available tasks, you can run `ansible-playbook playbook.yaml --list-tasks`, which will spit out:

```zsh
playbook: playbook.yaml

  play #1 (localhost): From bucketing raw data to augmenting it with `s2fos` classif    TAGS: []
    tasks:
      Bucketize raw files by decade     TAGS: [bucketize]
      Parse abstract from metadata files        TAGS: [parse_abstract]
      Create s2fos lookups      TAGS: [s2fos_lookups]
      Augment s2orc with s2fos classification   TAGS: [augment_s2orc_with_s2fos]

  play #2 (localhost): Querying `s2search` API based on keywords, then the `specter` API for their embeddings.  TAGS: []
    tasks:
      Run s2search API  TAGS: [run_s2search_data]
      Run specter API   TAGS: [run_specterAPI]

  play #3 (localhost): Projecting SPECTER embeddings into lower dimension and then clustering them.     TAGS: []
    tasks:
      Wrangle specterAPI data   TAGS: [wrangle_specter]
      Embeddings to 'topics'    TAGS: [top2vec]

```
Note that there are really 3 plays, one for wrangling data from the `s2orc` databse, query `s2search` database, and the last to perform SPECTER embeddings. The `s2orc` database was needed to have the yearly total number of documents in a field. But we needed the classification from `s2search` to make that happen. Now that we have the number of documents that have, say, the `computational` keyword with the total number of documents, we can normalize frequencies.

#### Notes:

 - 25-01-23: `run_specterAPI` still doesn't work out of the box. We still run `run_specterAPI.sh` field by field. Also the whole pipeline is still just in test mode. It doesn't affect the real data.
