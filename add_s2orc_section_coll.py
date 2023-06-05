import json
import time

import pandas as pd

from creds import client

db = client["papersDB"]

def get_relevant_journals():
    df_google=pd.read_csv("/home/jstonge/Documents/phd/side_quest/dark-data/etc/journalsbyfield.csv", names=['Publication', 'h5-index', 'h5-median'])
    df_google["Publication"] = df_google.Publication.str.lower()
    
    df_oa = pd.DataFrame(list(db.venues_oa.find(
        {}, 
        {"display_name": 1, "alternate_titles":1, "abbreviated_title": 1, "ids": 1}
    )))
    
    oa_display_name2googlepub = {
        'Applied Catalysis B-environmental': 'applied catalysis b: environmental',
        'Journal of energy & environmental sciences': 'energy & environmental science',
        'Journal of materials chemistry. A, Materials for energy and sustainability': 'journal of materials chemistry a',
        'The American Economic Review': 'american economic review',
        'Quarterly Journal of Economics': 'the quarterly journal of economics',
        'Journal of Finance': 'the journal of finance',
        'Physical Review X': 'physical review. x',
        'European Physical Journal C': 'the european physical journal c',
        'Nature Reviews Molecular Cell Biology': 'nature reviews. molecular cell biology',
        'Journal of Religion & Health': 'journal of religion and health',

    }

    df_oa['display_name_lower'] = df_oa.display_name.map(lambda x: oa_display_name2googlepub[x] if oa_display_name2googlepub.get(x) else x)
    df_oa["display_name_lower"] = df_oa.display_name_lower.str.lower()

    metadata_venue = df_google.merge(df_oa, how="left", left_on="Publication", right_on="display_name_lower")

    # missing venues, if anyone wants to keep looking for them in the db
    # missing_venues = metadata_venue[metadata_venue.display_name.isna()].Publication.tolist()
    # dropping nas. 171/180 left.
    return metadata_venue[~metadata_venue.display_name.isna()]


def parse_paragraph(paper, venue):
    paragraphs = json.loads(paper['content']['annotations']['paragraph'])
    out = []
    for i, p in enumerate(paragraphs):
        start, end = int(p['start']), int(p['end'])
        out.append({
            'corpusid': paper['corpusid'], 
            'venue': venue,
            'did': i, 
            'text': paper['content']['text'][start:end]
            })
    return out

def get_paper_by_venue(venue):
    return list(db.papers.find({"venue": venue}, {'corpusid': 1}))

def main():

    metadata_venue = get_relevant_journals()
    tot_venue = len(metadata_venue)
    i = 0
    for venue in metadata_venue.display_name:
        print(f"doing {venue} ({i} / {tot_venue})")
        metadata_paper_venue = get_paper_by_venue(venue)
        if len(metadata_paper_venue) > 0:
            papers = [db.s2orc.find_one({"corpusid": cid['corpusid']}) for cid in metadata_paper_venue]
            papers = [p for p in papers if p is not None]
    
            for i, b in enumerate(papers):
                if b['content']['text'] is not None and b['content']['annotations']['paragraph'] is not None:                   
                    db.s2orc_section.insert_many( parse_paragraph(b, venue) )
        
        i += 1

if __name__ == "__main__":
    main()