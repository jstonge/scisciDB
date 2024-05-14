
## SOS cli

### Installation

Install the `scisciDB` command line interface, called `sos`, using the following command:

```zsh
pip install ./scisciDB
```

Since it calls the mongoDB without authentification, you need to be on the `UVM` server for the CLI to work.

## Why?

We want to have full text of scientific works. The only way to do it at the moment is to upload `s2orc`. We want `s2orc` to be enriched with `openAlex` metadata. So we build that small library to facilitate the interoperability of `s2orc` and `openAlex`.

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
