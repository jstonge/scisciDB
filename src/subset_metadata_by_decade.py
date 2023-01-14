# Description: This script subsets bucketized metadata files in `metadata_by_decade/` to 
#              get only papers with abstract or pdf.
# Author: Jonathan St-Onge

import argparse
import re
from pathlib import Path

from jsonlines import jsonlines
from tqdm import tqdm


def main():
    """
    Extract papers from metadata_by_decade_all with either the pdf or abstract.
    
    We do a decade at a time.
    """
    S2ORC_DIR = Path()
    DIR_METADATA   = S2ORC_DIR / "output" / "metadata_by_decade_all"

    # decade = 1950
    # parse = 'abstract'
    fname = [_ for _ in DIR_METADATA.glob("*.jsonl")
             if re.search(f"metadata_{args.decade}_all.jsonl", str(_))][0]

    fname_short = re.sub(".jsonl", "", str(fname).split("/")[-1])
    OUT = DIR_METADATA / f'{fname_short}_simple_has_{args.parse}.jsonl'
    
    with jsonlines.open(fname) as reader:
        
        if args.parse == 'pdf':

            for line in tqdm(reader):
                
                if line['has_pdf_parse'] and line['has_pdf_parsed_body_text']:
                
                    if line.get('year') is not None and line.get('mag_field_of_study') is not None:
                                
                        # CALC NUMBER CITATIONS
                        # !TODO: to discuss citations overall vs s2orc only with others. 
                        if line['has_inbound_citations'] and line['has_outbound_citations']:
                            nb_citations_from_s2orc_papers = len(line['inbound_citations'])
                            nb_refs_from_s2orc_papers = len(line['outbound_citations'])
                        
                        else:
                            nb_citations_from_s2orc_papers = None
                            nb_refs_from_s2orc_papers = None
                        
                        with jsonlines.open(OUT, 'a') as writer:
                            writer.write({
                            'paper_id': line['paper_id'],
                            'title': line['title'],
                            'year': line['year'],
                            'mag_field': line['mag_field_of_study'],
                            's2_field': line.get('s2_field_of_study'),
                            'nb_citations': nb_citations_from_s2orc_papers,
                            'nb_refs': nb_refs_from_s2orc_papers
                            }
                        )
        
        elif args.parse == 'abstract':
            
            for line in tqdm(reader):
                
                if line.get('abstract') is not None:

                    if line.get('year') is not None and line.get('mag_field_of_study') is not None:
                        
                        with jsonlines.open(OUT, 'a') as writer:
                            writer.write({
                                'paper_id': line['paper_id'],
                                'title': line['title'],
                                'year': line['year'],
                                'mag_field': line['mag_field_of_study'],
                                's2_field': line.get('s2_field_of_study'),
                                'abstract': line['abstract']
                                })
        
        else:
            print("Unknown parse type. It should be pdf or abstract.")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--decade", type=int)
    parser.add_argument('--parse') 
    args = parser.parse_args()
    
    main()
