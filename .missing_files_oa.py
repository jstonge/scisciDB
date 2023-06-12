import json
import re
from pathlib import Path
import sys

data_path = Path(sys.argv[2])

def get_all_files_oa():
    with open(data_path / "manifest") as f:
        dat = json.loads(f.read())
    return set([re.sub("(s3://openalex/data/works/|\.gz)", "", _['url']) for _ in dat['entries'] if len(re.split("/")) == 2])

def get_done_files_oa():
    return set([str(path) for path in data_path.rglob('*') if len(re.split("/", str(path))) == 2])

def get_missing_files_oa():
    print(get_all_files_oa() - get_done_files_oa())

