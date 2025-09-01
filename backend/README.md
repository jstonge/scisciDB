# SciSciDB Backend

Python backend for the Science of Science Database toolkit. Handles downloading datasets from academic APIs, storing them in MongoDB, and exporting data for frontend visualization.

## Architecture Overview

```
Academic APIs → Download → MongoDB → Export → Static JSON → Frontend
```

The backend provides three main functions:
1. **Download** datasets from Semantic Scholar, OpenAlex, etc.
2. **Upload** datasets to MongoDB with smart deduplication
3. **Export** curated data as static JSON files for the frontend

## Project Structure

```
backend/
├── sciscidb/                    # Main Python package
│   ├── __init__.py
│   ├── config.py               # Environment & path configuration
│   ├── download.py             # Download from academic APIs
│   ├── upload.py               # Upload to MongoDB
│   ├── database.py             # MongoDB connection & basic queries
│   └── export.py               # Export data for frontend
│
├── scripts/                    # CLI tools
│   ├── download_data.py        # Download datasets
│   ├── upload_data.py          # Upload to MongoDB
│   └── export_data.py          # Export for frontend
│
└── README.md                   # This file
```

## Installation & Setup

### 1. Environment Setup

```bash
# Required environment variables
export S2_API_KEY="your_semantic_scholar_api_key"
export MONGO_URI="mongodb://username:password@host:port/?authSource=admin"

# Data path to scisciDB
export SCISCI_DATA_PATH="/netfiles/compethicslab/scisciDB/semanticscholar"
```

### 2. Install Dependencies

```bash
uv sync
source .venv/bin.activate
```

## CLI Database Operations

The backend provides powerful CLI tools for exploring and analyzing your data without writing code.

### Basic Database Operations

```bash
# Test database connection
python scripts/db_operations.py test-connection

# List all collections
python scripts/db_operations.py list-collections

# Count documents (fast estimates)
python scripts/db_operations.py count --collection papers
python scripts/db_operations.py count --all

# Exact counts (slower but precise)
python scripts/db_operations.py count --collection papers --exact

# Explore data structure
python scripts/db_operations.py sample --collection papers
```

### Group Count Analysis

Perform fast aggregations on large datasets with sampling:

```bash
# Top venues by paper count
python scripts/db_operations.py group-count --collection papers --field venue

# Papers by publication year
python scripts/db_operations.py group-count --collection papers --field year --limit 30

# Fast analysis with 10k sample (seconds instead of minutes)
python scripts/db_operations.py group-count --collection papers --field venue --fast
```

### Filtered Analysis

Combine filtering with grouping for targeted analysis:

```bash
# Nature papers by year
python scripts/db_operations.py group-count \
  --collection papers \
  --field year \
  --filter-field venue \
  --filter-value "Nature"

# Publication types in 2023
python scripts/db_operations.py group-count \
  --collection papers \
  --field publicationtypes \
  --filter-field year \
  --filter-value "2023"

# Top venues for recent papers
python scripts/db_operations.py group-count \
  --collection papers \
  --field venue \
  --filter-field year \
  --filter-value "2024" \
  --limit 50
```

### Performance Options

Choose speed vs accuracy based on your needs:

| Option | Sample Size | Time (200M papers) | Accuracy |
|--------|-------------|-------------------|----------|
| `--fast` | 10,000 | 2-5 seconds | ±15% |
| Default | 50,000 | 5-15 seconds | ±5% |
| `--sample 100000` | 100,000 | 10-30 seconds | ±3% |
| `--exact` | All documents | 30-300 seconds | Exact |
