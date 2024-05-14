import json
import re

import pandas as pd

from creds import client

from jsonlines import jsonlines
from bson import json_util
from tqdm import tqdm

def main():
    db = client['papersDB']
    
    # subset = list(db.papers.aggregate([{'$sample': {'size': 10_000}}]))
    
    # df_subset = pd.DataFrame(subset)
    # df_subset['field'] = df_subset['s2fieldsofstudy'].map(lambda x: x[0]['category'] if x else None)
    
    # df_subset = df_subset.groupby('field').head(10_000)

    # text_subset = []
    # for cid in tqdm(df_subset.corpusid.tolist()):
    #      text_subset.append(db.s2orc.find_one({'corpusid': cid}))

    # text_subset = [t for t in text_subset if t is not None]

    # res = {}
    # for i,paper in enumerate(text_subset):
    #     sec_headers = paper['content']['annotations']['sectionheader']
    #     if sec_headers is not None:
    #         start_headers = [int(_) for _ in re.findall('(?<=start\":)\d+', sec_headers)]
    #         tot_sections = len(start_headers)-1
    #         if paper['content']['annotations']['paragraph'] is not None:
    #             section = 1
    #             for start, end in zip(start_headers[:-1], start_headers[1:]):
    #                 text = paper['content']['text'][start:(end-1)]
    #                 res.update({(paper['corpusid'], f'{section}/{tot_sections}'): text})
    #                 section += 1

    # df = pd.DataFrame({
    #     'corpusid': [_[0] for _ in res.keys()], 
    #     'section': [_[1] for _ in res.keys()], 
    #     'text': list(res.values())
    #     })


    # df = df[df.text.str.contains(' data ')]
    # df['text'] = df.text.str.split('\n\n')
    # df = pd.DataFrame.explode(df, 'text')
    # df = df[df.text.str.contains(' data ')]
    # df['text'] = df.text.map(lambda x: ' '.join(["**"+w+"**" if w == 'data' else w for w in re.split(" ", x)]))

    # df = df.reset_index()

    # df['subsection'] = df.groupby(['corpusid', 'section'])['index'].rank(method="first", ascending=True)
    # df = df.loc[:, ['corpusid', 'section', 'subsection', 'text']]
    # df['wc'] = df.text.str.split(" ").map(len)
    # df = df.merge(df_subset, how='left', on='corpusid')

    # df.to_csv("data_statements_to_lab.csv", index=False)

    #!TODO: using batch and next on aggregate
    # cur = db.s2orc.aggregate([
    #     {"$sample": {"size": 250_000} },
    #     { "$project": {
    #         "corpusid": 1,
    #         "sectionsWithData": {
    #             "$regexFindAll": { "input": "$content.text", "regex": "\n\n(.+?) data.+?\n\n"}
    #             }
    #         }
    #     }
    # ])
    
    # with open('data_statements_to_embed.jsonl', 'w') as fout:
    #     for batch in tqdm(cur.batch_size(100)):
    #         if batch['sectionsWithData']:
    #             json.dump(json.loads(json_util.dumps(batch)), fout)
    #             fout.write('\n')
    
    # data = []
    # with jsonlines.open('data_statements_to_embed.jsonl') as f:
    #     for obj in f:
    #         data.append(obj)
    #         # break
    #         db.papers.find_one({"corpusid": data[0]['corpusid']})
    
    # Conclusion: takes too long to find the corpusid without additional information
    #             in papers collection. Cheaper to find corpus ids in s2orc coll.
    #             Maybe if we could add papers metadata to s2orc coll...
            

if __name__ == '__main__':
    main()
