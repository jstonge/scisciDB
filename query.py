import json
import re
from collections import Counter
from pathlib import Path

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from jsonlines import jsonlines
from tqdm import tqdm

sns.set_style("whitegrid")

ROOT_DIR = Path(".")
DIR_METADATA = ROOT_DIR / "20200705v1" / "full" / "metadata"
DIR_ABSTRACTS = ROOT_DIR / "20200705v1" / "full" / "abstracts"
DIR_PDF = ROOT_DIR / "20200705v1" / "full" / "pdf_parses"
DIR_PDF_METHO = ROOT_DIR / "20200705v1" / "full" / "pdf_parses_metho"
ALEX_PATH = Path("../openalex")

def flatten(l):
    return [item for sublist in l for item in sublist]


# OPTION 1: CLASSIFY ABSTRACT USING LABELED DATA -----------------------------------------------

# S2ORC_GOLD comes from OPENALEX script. IT means we have
# the authors' INSTITUTIONS, the BODYTEXT, and the ABSTRACT
# all in the same object. The file also contain identifier
# from both database (s2orc and open alex).
#
# The results have not been validated.

with jsonlines.open('20200705v1/s2orc_gold.jsonl') as reader:
        m_id = { line['paper_id'] : {
        'title': line['title'],
        'year': line['year'],
        'authorships': line['authorships'],
        'journal': line['journal'],
        'concepts': line['concepts']
        } for line in reader }

for file in DIR_PDF.glob("*.jsonl"):
    print(f'Doing {file}')

    metho_path = re.sub("pdf_parses", "pdf_parses_metho", str(file))

    with jsonlines.open(file) as reader:
        for line in tqdm(reader):

            if m_id.get(line['paper_id'] ) is not None:
                metadata = m_id[line['paper_id']]
                metho = [
                        p for p in line['body_text']
                        if bool(re.match('data', p['section'], re.IGNORECASE))
                ]

                if len(metho) > 0:

                    with jsonlines.open(metho_path, 'a') as writer:
                        writer.write(
                            {'paper_id': line['paper_id'],
                             'title': metadata['title'],
                             'year': metadata['year'],
                             'journal' : metadata['journal'],
                             'authorships': metadata['authorships'],
                             'concepts': metadata['concepts'],
                             'body_text': metho}
                        )


# OPTION 2: EXTRACT GIT_HUB URL ----------------------------------------------------------------



# OPTION 3: CLASSIFY METHODOLOGY USING LABELED DATA --------------------------------------------

method_sections = ['method', 'data', 'open access', 'statistical analysis']

analysis_snippet = ['We analyze ...']

# OPTION 4: CLASSIFY CAPTION USING LABELED DATA ------------------------------------------------

# We want to identify simulation/theoretical papers potentially with code.



# ------------------------ Which papers comp titles ------------------------ #


def get_title_paper_type(keywords_re, only_title = True):
    """
    GET TITLE PAPER TYPE
    
    Custom keyword search based on exact matching in title. 
    
    The only "preprocessing step" is that we ignore the case. We do not account for other ways
    to write the query (no fuzzy or elastic search). 
    
    The results have not been validated.
    """
    S2ORC_DIR = Path()
    DIR_METADATA_BY_DECADE = S2ORC_DIR / "metadata_by_decade"
    
    files = list(DIR_METADATA_BY_DECADE.glob("*jsonl"))
    relevant_articles = []
    for i, f in enumerate(files):
        print(f'Done {i+1}/{len(files)} files')
        with jsonlines.open(f) as reader:
            print(f"Doing {f}")
            if only_title:
                for line in tqdm(reader):
                    if re.match(keywords_re, line["title"], flags=re.IGNORECASE):
                        relevant_articles.append(line)
            else:
                for line in tqdm(reader):
                    if re.match(keywords_re, line["title"], flags=re.IGNORECASE) or \
                        (line.get("abstract") is not None and re.match(keywords_re, line["abstract"], flags=re.IGNORECASE)):
                        relevant_articles.append(line)


    return relevant_articles


keywords_re = "(computation|digital humanities|cultural analytic)"
comp_papers = get_title_paper_type(keywords_re) 
comp_papers_w_abstract = get_title_paper_type(keywords_re, only_title=False) 

no_comp_title = [_ for _ in comp_papers_w_abstract 
                 if bool(re.match(keywords_re, _["title"], flags=re.IGNORECASE)) is False]

rel_yrs = [_[1] for _ in nb_paper_by_yr]
rel_yrs = sorted(pd.unique(rel_yrs))

# count by decade
comp_title_by_yr = []
for year in rel_yrs:
    comp_title_by_yr.append([_ for _ in comp_papers_w_abstract if _['year'] == year])


# Count by field
out = {}
for paper in comp_papers_w_abstract:
    if paper.get("mag_field_of_study") is not None:
        for field in paper["mag_field_of_study"]:
            if out.get(field) is None:
                out[field] = 1
            else:
                out[field] += 1

# count by field and decade
out = {}
for paper in comp_papers_w_abstract:
    if paper.get("mag_field_of_study") is not None:
        for field in paper["mag_field_of_study"]:
            if out.get((field,paper['year'])) is None:
                out[(field,paper['year'])] = 1
            else:
                out[(field,paper['year'])] += 1


# nb_articles_by_decade = [17890, 43895, 96268, 177638, 490391, 1933137, 4880964, 15307]
# sum(nb_articles_by_decade)


y = [len(x1) / norm_x1  for x1, norm_x1 in zip(comp_title_by_yr, nb_paper_by_yr.values())]
x = [_ for _ in rel_yrs]
sns.barplot(x, y)

y = [y1 for y1 in out.values()]
x = [x1[1] for x1 in out.keys()]
xgroup = [x1[0] for x1 in out.keys()]

df = pd.DataFrame({"yr":x, "val":y, "discipline":xgroup})\
       .set_index(['discipline','yr'])['val']\
       .unstack(fill_value=0).stack()\
       .reset_index(name='val')

df["3yrs"] = df.yr - df.yr % 3

agg_data = df.groupby("3yrs")["val"].sum().reset_index()

df = df.merge(agg_data, how="left", on="3yrs", suffixes=["_yearly", "_tot"])\
       .assign(pct = lambda x: x.val_yearly / x.val_tot * 100)

# Draw a nested barplot by species and sex
# g = sns.catplot(
#     data=df, kind="bar",
#     y="discipline", x="pct", hue="3yrs",
#     palette="dark", alpha=.6, height=6
# )

# g.despine(left=True)
# g.set_axis_labels("", "")
# g.legend.set_title("")
# plt.savefig("p3.pdf", width=12, height=12)

sns.lmplot(x="3yrs", y="pct", hue="discipline", lowess=True, data=df,
height=6, aspect=1.5)
plt.savefig("p4.pdf")

# 17890+43895+96268+177638+490391+1933137+4880964+15307 = 7_655_490


# ----------------------------- All fields search ---------------------------- #



def search_all_fields(query):
    """
    SEARCH ALL FIELDS IN METADATA

    Custom keyword search based on exact matching in 
    title, abstract, or journal. The only "preprocessing step"
    is that we ignore the case. We do not account for other ways
    to write the query (no fuzzy or elastic search).
    
    The results have not been validated.
    """
    files = list(DIR_METADATA.glob("*jsonl"))
    relevant_articles = []
    for i, f in enumerate(files):
        print(f'Done {i+1}/{len(files)} files')
        with jsonlines.open(f) as reader:
            for line in tqdm(reader):
                if re.match(query, line["title"], flags=re.IGNORECASE):
                    relevant_articles.append(line)
                elif line.get('abstract') is not None:
                    if re.match(query, line["abstract"], flags=re.IGNORECASE):
                        relevant_articles.append(line)
                elif line.get('journal') is not None:
                    if re.match(query, line["journal"], flags=re.IGNORECASE):
                        relevant_articles.append(line)
                    
    return relevant_articles

css = search_all_fields("computational social science")

len(css)


# EXTRA: COUNT ALL SECTION NAMES ---------------------------------------------------------------


def count_section_names(batch):
    """Only for the relevant papers"""
    with open(DIR_ABSTRACTS / f'abstract_{batch}.jsonl') as f_meta:
        for line in f_meta:
            m_id = {int(m['paper_id']): m['journal'] for m in json.loads(line)}

    with open(DIR_PDF / f'pdf_parses_{batch}.jsonl') as f_pdf:
        sections = []
        for line in tqdm(f_pdf):
            d = json.loads(line)

            # suppose we only care about papers in m_id
            if m_id.get( int(d['paper_id']) ) is None:
                continue

            sections.append([
                p['section'].lower() for p in d['body_text'] if len(p['section']) > 0
            ])

        section_counter = Counter( flatten(sections) )
        TOP_PCT = round(len(section_counter) * .001)

        with open(DIR_METADATA / 'all_section_names_count.txt', "a") as f:
            [f.write(f'{_[0]}, {_[1]}\n') for _ in section_counter.most_common(TOP_PCT)]




[count_section_names(batch=i) for i in range(100)]

def read_section_names():
    out = []
    with open(DIR_METADATA / "all_section_names_count.txt") as f:
        out.append(f.read().split("\n"))

    df = pd.DataFrame(out[0]).iloc[:,0].str.split(", (?=\d)", expand=True)\
           .rename(columns={0:'section_name', 1:'n'})\
           .dropna().assign(n = lambda x: x.n.astype(int))
    
    return df

def clean_section_name():
    ONLY_NUM_RE = "^\d{1,3}"
    ROMAN_SECTION_RE = "^[iv]+\.? "
    NUMERAL_SECTION_RE = "[1-9]+\. "
    NON_ALPHA = '[^a-zA-Z]+'
    THRESH_NAME_LEN = 3

    df = read_section_names()
    df = df[~df.section_name.str.contains(ONLY_NUM_RE)]
    df.section_name = df.section_name.str.replace(ROMAN_SECTION_RE, "", regex=True)
    df.section_name = df.section_name.str.replace(NUMERAL_SECTION_RE, "", regex=True)
    df.section_name = df.section_name.str.replace(NON_ALPHA, ' ', regex=True).str.strip()
    df = df[df.section_name.map(len) > THRESH_NAME_LEN]
    df = df.groupby('section_name').sum().sort_values('n', ascending=False).reset_index()

    return df

def plot_section_name():
    df = clean_section_name()
    f, p = plt.subplots(1,1, figsize=(10,50))
    sns.barplot(x='n', y='section_name', data=df[df.n > 300], color='k')
    plt.ylabel(None)
    plt.xscale('log')
    plt.yticks(fontsize=10)
    sns.despine()
    plt.savefig(DIR_METADATA / "section_names.pdf",  bbox_inches='tight');

plot_section_name()


# ----------------------------- bucketized_S2orc ----------------------------- #



                
def bucketized_S2orc():
    S2ORC_DIR = Path()
    OUTPUT_DIR   = S2ORC_DIR / "metadata_by_decade"

    dois = []
    decade = []
    discipline = []

    counter_failed = 0
    files = list(OUTPUT_DIR.glob("*jsonl"))
    for i, f in enumerate(files):
        print(f'Done {i+1}/{len(files)} files')
        with jsonlines.open(f) as reader:
            for line in tqdm(reader):
                if line['doi'] is not None and line['year'] is not None and line['mag_field_of_study'] is not None:
                    dois.append(line['doi'])
                    decade.append(line['year'] - line['year'] % 10)
                    discipline.append(line['mag_field_of_study'])
                else:
                    counter_failed += 1


    len(decade)
    len(dois)
    len(discipline)

    df = pd.DataFrame({'decade': decade, 'discipline':discipline, 'doi': dois})
    
    df = df.explode('discipline')

    df.to_csv("metadata_by_decade_and_fields.csv")





# ------------------------------- extract url -------------------------------- #


def which_paper_has_abstract():
    S2ORC_DIR = Path()
    DIR_METADATA_BY_DEACADE  = S2ORC_DIR / "metadata_by_decade_all"
    DIR_OUTPUT = S2ORC_DIR / "20200705v1" / "metadata_with_abstract"

    files = list(DIR_METADATA_BY_DEACADE.glob("*jsonl"))
    out = []
    for i, f in enumerate(files):
        print(f'Done {i+1}/{len(files)} files')
        with jsonlines.open(f) as reader:
            for line in tqdm(reader):
                if line['has_pdf_parse']:
                    out.append(line['paper_id']) 
        
paper_ids = which_paper_has_abstract()


def bucketized_S2orc_all():
    S2ORC_DIR = Path()
    DIR_METADATA_BY_DEACADE   = S2ORC_DIR / "metadata_by_decade_all"
    
    files = list(DIR_METADATA_BY_DEACADE.glob("*jsonl"))
    for i, f in enumerate(files):
        print(f'Done {i+1}/{len(files)} files')
        with jsonlines.open(f) as reader:
            for line in tqdm(reader):
                if line.get('year') is not None:
                    decade = line['year'] - line['year'] % 10
                    if (decade >= 1950) and (line['year'] <= 2022):
                        OUT = DIR_METADATA_BY_DEACADE / f'metadata_{decade}.jsonl'
                        with jsonlines.open(OUT, 'a') as writer:
                            writer.write(line)

bucketized_S2orc_all()