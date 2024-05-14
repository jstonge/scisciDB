"""
Command Line Interface (CLI) for cat-project.
Note that this script should be as thin as possible
to allow most of the testing to be directed at the API
"""
from contextlib import contextmanager
from typing import List
import spacy # for tokenization and other NLP tasks
from pathlib import Path
import json

from typing_extensions import Annotated
from rich.table import Table
from rich.progress import track
from rich.console import Console
from rich.table import Table

from kitty import Text
import kitty

import typer

console = Console()
app = typer.Typer(add_completion=False)


@app.command()
def version():
    """Return version of chat application"""
    kitty_ascii = f"""
    \    /|     kitty cli
     )  ( ')
    (  /  )
     \(__)|     version {kitty.__version__}
    =========================
    """
    print(kitty_ascii)

@app.command("list")
def list_institutions(verbose: Annotated[bool, typer.Option("--verbose")] = False):
    """
    List institutions in db.
    """
    with kitty_db() as db:
        
        # ror -> pdf_count
        ror2catalog=db.count(by="inst_id", collection="cc_catalog")
        
        if verbose:
            # get dictionaries ror -> other info
            ror2pdf = db.count(by="inst_id", collection="cc_pdf")   # ror -> catalog_count
            ror2png = db.count(by="inst_id", collection="cc_png") # ror -> png
            ror2text = db.count(by=["inst_id", "conversion"], collection="cc_text") # ror -> text
            ror2name = db.get_ror2name(rors=ror2catalog.keys()) # ror -> display_name
            
            # Summarize everything
            table = Table("index", "ror", "display name", "#Catalog",  "#PDF", "#PNG", "#Text(fitz)", "#Text(paddleOCR)")
            for i,(k,v) in enumerate(ror2catalog.items()):
                # making sure there is no None
                paddleOCR_count = str(0) if ror2text.get((k,'paddleOCR')) is None else str(ror2text[(k,'paddleOCR')])
                fitz_count = str(0) if ror2text.get((k,'fitz'))is None else str(ror2text[(k,'fitz')])
                # add rows
                table.add_row(str(i), k, ror2name[k], str(v), str(ror2pdf[k]), 
                              str(ror2png[k]), fitz_count, paddleOCR_count)

        else:
            table = Table("index", "ror", "#Catalog")
            for i,(k,v) in enumerate(ror2catalog.items()):
                table.add_row(str(i), k, str(v))
            
        console.print(table)

@app.command("reset")
def reset_institution(inst_id: str):
    """
    Remove all collections associated with the specified ROR from the dB.
    """
    with kitty_db() as db:
        db.reset_institution(inst_id)

@app.command("token")
def token_over_time(inst_id: str, token: str, converter: str = 'fitz'):
    """
    List the count of given token each year for a given ror.
    """
    with kitty_db() as db:
        res=db.find(inst_id, agg_field="inst_id", collection="cc_catalog")
        out = []
        for r in res:
            if 'tokens' in r:
                if converter in r['tokens']:
                    if token in r['tokens'][converter]:
                        out.append(
                            { "year": r['metadata']['start_year'],
                              "token": token,
                              "count": r['tokens'][converter][token],
                              "total_count": sum(list(r['tokens'][converter].values())),
                              "cat_metadata": r['metadata']
                            }
                        )
        fout = Path(f'{inst_id}_{token}.json')
        with open(fout, 'w') as f:
            json.dump(out, f)

@app.command("upload_text")
def upload_text(inst_id: str, converter: str):
    """
    Upload texts db for a whole institution.
    """
    with kitty_db() as db:
        try:
            # If the total number of (PNGs + PDFs) for a given institution
            # is equal to the number of texts for a given converter, then we consider it as done.
            pdf_cat = db.find(inst_id, agg_field="inst_id", collection="cc_pdf")
            png_cat = db.find(inst_id, agg_field="inst_id", collection="cc_png")
            text_cat = list(db._db._db["cc_text"].find({
                "metadata.inst_id": inst_id, "metadata.conversion": converter
                }))
            
            if (len(pdf_cat)+len(png_cat)) == len(text_cat):
                print(f"All texts from {inst_id} are already uploaded")
            
            else:    
                for i, r in track(enumerate(pdf_cat), total=len(pdf_cat)):
                    # If the number of (PNGs + Full Page) for a given PDF
                    # is equal to the number of texts for a given converter, then we consider it as done.
                    png_cat_i = db.find(r['id'], agg_field="pdf_id", collection="cc_png") 
                    text_cat_i = list(db._db._db["cc_text"].find({
                        "metadata.pdf_id": r['id'], "metadata.conversion": converter
                    }))
                    if (len(png_cat_i)+1) == len(text_cat_i):
                        pass
   
                    # get texts, this step takes some time when converter are OCR
                    # because we need to OCR each page individually. Perhaps we could
                    # parallelize this step at some point.
                    texts = db.convert2text(r['id'], converter)
                    
                    # update text page by page
                    for i, text in enumerate(texts):
                        db.upload(
                            Text(id=r['id']+"_"+str(i)+"_"+converter, 
                                 inst_id=inst_id, text=text,
                                 catalog_id=r['metadata']['catalog_id'], 
                                 pdf_id=r['id'], 
                                 png_id=r['id']+"_"+str(i), 
                                 conversion=converter,
                                 page=i, 
                                 annotated=False)
                                )
                        
                    # update text full catalog
                    db.upload(
                            Text(id=r['id']+"_"+converter, 
                                 inst_id=inst_id, text=" ".join(texts),
                                 catalog_id=r['metadata']['catalog_id'], 
                                 pdf_id=r['id'], 
                                 png_id=r['id'], 
                                 conversion=converter,
                                 page='full', annotated=False)
                        )

        except kitty.api.InvalidCatId:
            print(f"Error: Invalid card id {inst_id}")

@app.command("update_ngrams")
def update_ngrams(inst_id: str, converter: str, ngrams: Annotated[List[int], typer.Option()] = [1]):
    """
    Update 'cc_catalog' with ngrams of clean text for a given ROR and converter. 
    """
    with kitty_db() as db:
        try:
            # Calculate length of texts_obj in advance for progress bar.
            texts_obj = [_ for _ in db.find(id=inst_id, agg_field="inst_id", collection="cc_text") 
                         if _['metadata']['page'] == 'full' 
                         and _['metadata']['conversion'] == converter]

            # Hardcoded. But it could be an argument.
            nlp = spacy.load("en_core_web_sm", disable=['ner'])

            # TODO: This could be parallelized..
            for obj in track(texts_obj, total=len(texts_obj)):
                catalog_id = obj['metadata']['catalog_id']
                clean_text = db.clean_text(obj['text'], nlp)
                db.update_ngrams(catalog_id, clean_text, 'fitz', ngrams, nlp)

        except kitty.api.InvalidCatId:
            print(f"Error: Invalid card id {inst_id}")

@app.command("upload_png")
def upload_pngs(inst_id: str):
    """
    Upload PNGs from PDFs for a specified ROR from the dB.
    """
    with kitty_db() as db:
        try:
            print("loading pdfs and their metadata")
            pdfs = db.find_gridfs(inst_id, agg_field="inst_id", collection="cc_pdf")
            pdf_meta = db.find(inst_id, agg_field="inst_id", collection="cc_pdf")
            
            # assuming they are in the same order (they should);
            for pdf_meta, pdf_file in track(zip(pdf_meta, pdfs), total=len(pdf_meta)):
                db.upload_from_pdf(pdf_file, pdf_meta)

        except kitty.api.InvalidCatId:
            print(f"Error: Invalid card id {inst_id}")

@app.command("summarize_text")
def text_summary(id: str, converter: str = 'fitz', do_clean: Annotated[bool, typer.Option("--do_clean")] = False):
    """
    Provide count types and values for a given ROR or PDF id.
    """
    def extract_year(dictionary):
        # Split the string on underscores and take the third part (index 2), then split by "_" and take the first part for the year
        year_part = dictionary["id"].split("_")[2]
        # Extract the year (first 4 characters of the year_part)
        year = int(year_part[:4])
        return year

    agg_field = "inst_id" if len(id.split("_")) == 1 else "pdf_id"

    with kitty_db() as db:
        table = Table("id", "#Types", "#Tokens", "Top10")
        if agg_field == 'inst_id':
            pdf_obj = db.find(id, agg_field, collection="cc_pdf")
            sorted_pdf_obj = sorted(pdf_obj, key=extract_year)
        elif agg_field == 'pdf_id':
            sorted_pdf_obj =  [db.find_one(id, agg_field=None, collection="cc_pdf")]

        for pdf in track(sorted_pdf_obj, total=len(sorted_pdf_obj)):
            text_summary = db.text_summary(pdf['id'], 'pdf_id', converter, do_clean)
            table.add_row(pdf['id'], str(text_summary['types']), str(text_summary['tokens']), ", ".join(list(text_summary['text_count'].keys())))
            
        console.print(table)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Kitty is a small command line for the Cat-Project application.
    """
    if ctx.invoked_subcommand is None:
        list_institutions()


@contextmanager
def kitty_db():
    # db_path = get_path()
    db = kitty.catDB()
    yield db


if __name__ == "__main__":
    app()
