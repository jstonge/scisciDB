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

## Key Features

### Smart Environment Detection
- **HPC Mode**: Auto-detects `/netfiles` and uses group directories
- **Local Mode**: Uses project-relative paths for development
- **Path Resolution**: Handles dataset name variations automatically

### Intelligent ID Field Detection
Different Semantic Scholar datasets use different ID fields:
- **Papers**: `corpusid`
- **Authors**: `authorid` 
- **Venues**: `venueid`
- **Abstracts**: `corpusid`

The upload system automatically detects and uses the correct field.

### Robust File Processing
- Handles both `.json` and `.json.gz` files
- Supports JSON Lines and regular JSON formats
- Graceful error handling and duplicate management

## Installation & Setup

### 1. Environment Setup

```bash
# Required environment variables
export S2_API_KEY="your_semantic_scholar_api_key"
export MONGO_URI="mongodb://username:{pw}@host:port/?authSource=admin"

# Optional: Custom data path (auto-detected on HPC)
export SCISCI_DATA_PATH="/netfiles/compethicslab/scisciDB/semanticscholar"
```

### 2. Install Dependencies using `uv`

```bash
uv sync
```

## Usage

### Download Datasets

Note: You need you're own API key to replicate the workflow.

```bash
# Download papers dataset
python scripts/download_data.py papers --clean-slate

# Download authors dataset  
python scripts/download_data.py authors

# List available datasets
python scripts/download_data.py --list

# Check what's already downloaded
python scripts/download_data.py papers --info
```

### Upload to MongoDB

```bash
# Upload with auto-detected paths
python scripts/upload_data.py -i papers -c papers --clean-slate
python scripts/upload_data.py -i authors -c authors --clean-slate
python scripts/upload_data.py -i publication-venues -c publication-venues --clean-slate

# Upload from custom path
python scripts/upload_data.py -i /path/to/data/ -c my_collection
```

### Export for Frontend

```bash
# Explore data structure first
python scripts/export_data.py --explore

# Export all datasets
python scripts/export_data.py

# Export directly to frontend
python scripts/export_data.py --frontend /path/to/frontend/static/data/
```

## Data Flow

### 1. Download Process
```python
# Downloads from Semantic Scholar API
papers_path = download_semantic_scholar("papers", clean_slate=True)
# → /netfiles/compethicslab/scisciDB/semanticscholar/papers/papers_1.json, papers_2.json, ...
```

### 2. Upload Process  
```python
# Smart ID detection and MongoDB upload
stats = upload_to_mongodb(papers_path, "papers", clean_slate=True)
# → Creates unique index on 'corpusid', inserts ~2M papers
```

### 3. Export Process
```python
# Generate static JSON for frontend
export_all_datasets()
# → exports/papers_sample.json, venue_timeline.json, top_venues.json
```
## Performance Considerations

- **Large files**: Uses streaming downloads and chunked processing
- **Memory usage**: Processes files one at a time, not all in memory
- **Database**: Uses bulk inserts and unique indexes for efficiency
- **Deduplication**: MongoDB-level unique constraints, not application-level