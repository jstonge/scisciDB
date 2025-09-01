"""
Download datasets from various sources (Semantic Scholar, OpenAlex, etc.)
"""
import subprocess
import os
from pathlib import Path
from typing import Optional, List
import shutil

from .config import config

class DownloadError(Exception):
    """Exception raised when download fails"""
    pass

"""
Download datasets from various sources (Semantic Scholar, OpenAlex, etc.)
"""
import requests
import json
import gzip
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urlparse
import time

from .config import config

class DownloadError(Exception):
    """Exception raised when download fails"""
    pass

def download_semantic_scholar(dataset_name: str, clean_slate: bool = False) -> Path:
    """
    Download dataset from Semantic Scholar API
    
    Args:
        dataset_name: Name of dataset (papers, authors, publication-venues, etc.)
        clean_slate: Whether to remove existing data first
        
    Returns:
        Path to downloaded dataset directory
        
    Raises:
        DownloadError: If download fails
    """
    print(f"Downloading Semantic Scholar dataset: {dataset_name}")
    
    # Check if API key is set
    if not config.semantic_scholar_key:
        raise DownloadError("S2_API_KEY environment variable not set")
    
    # Setup paths
    dataset_path = config.get_dataset_path(dataset_name)
    
    # Handle clean slate
    if clean_slate and dataset_path.exists():
        print(f"Removing existing directory: {dataset_path}")
        import shutil
        shutil.rmtree(dataset_path)
    
    # Create directory
    dataset_path.mkdir(parents=True, exist_ok=True)
    print(f"Creating directory: {dataset_path}")
    
    # Setup API headers
    headers = {"x-api-key": config.semantic_scholar_key}
    
    try:
        # 1. Get latest release information
        print("Fetching release information...")
        releases_url = "https://api.semanticscholar.org/datasets/v1/release/"
        
        response = requests.get(releases_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        releases = response.json()
        if not releases:
            raise DownloadError("No releases found")
        
        # Get latest release (last in the array)
        latest_release = releases[-1]
        print(f"Latest release ID: {latest_release}")
        
        # 2. Get dataset file URLs
        dataset_url = f"https://api.semanticscholar.org/datasets/v1/release/{latest_release}/dataset/{dataset_name}"
        
        print(f"Downloading {dataset_name} dataset from release {latest_release}...")
        response = requests.get(dataset_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        dataset_info = response.json()
        
        # Save dataset metadata temporarily
        metadata_file = dataset_path / f"{dataset_name}.json"
        with open(metadata_file, 'w') as f:
            json.dump(dataset_info, f, indent=2)
        
        print(f"Successfully downloaded {metadata_file}")
        
        # 3. Extract and download individual files
        if 'files' not in dataset_info:
            raise DownloadError(f"No 'files' field found in dataset response")
        
        file_urls = dataset_info['files']
        if not file_urls:
            raise DownloadError("No files found in dataset")
        
        print(f"Found {len(file_urls)} files to download")
        
        # Download each file
        for i, url in enumerate(file_urls, 1):
            print(f"Downloading file {i}/{len(file_urls)}: {url}")
            
            # Determine filename based on URL extension
            parsed_url = urlparse(url)
            filename = f"{dataset_name}_{i}"
            
            if parsed_url.path.endswith('.json.gz'):
                downloaded_file = dataset_path / f"{filename}.json.gz"
                final_file = dataset_path / f"{filename}.json"
            else:
                downloaded_file = dataset_path / f"{filename}.json"
                final_file = downloaded_file
            
            # Download file
            try:
                file_response = requests.get(url, timeout=300, stream=True)
                file_response.raise_for_status()
                
                # Determine if file is compressed by checking content headers
                content_type = file_response.headers.get('content-type', '')
                content_encoding = file_response.headers.get('content-encoding', '')
                
                # Check if it's compressed
                is_compressed = (
                    'gzip' in content_type.lower() or
                    'gzip' in content_encoding.lower() or
                    parsed_url.path.endswith('.json.gz') or
                    parsed_url.path.endswith('.gz')
                )
                
                # Set filenames based on compression detection
                if is_compressed:
                    downloaded_file = dataset_path / f"{filename}.json.gz"
                    final_file = dataset_path / f"{filename}.json"
                else:
                    downloaded_file = dataset_path / f"{filename}.json"
                    final_file = downloaded_file
                
                # Write to file
                with open(downloaded_file, 'wb') as f:
                    for chunk in file_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = downloaded_file.stat().st_size
                print(f"  ✓ Downloaded {downloaded_file.name} ({file_size / 1024 / 1024:.1f} MB)")
                
                # If we detected compression, try to decompress
                if is_compressed and downloaded_file.name.endswith('.json.gz'):
                    print(f"  Decompressing {downloaded_file.name}...")
                    try:
                        # Test if it's actually compressed by trying to read it
                        with gzip.open(downloaded_file, 'rt', encoding='utf-8') as gz_file:
                            # Read just a small chunk to test
                            test_chunk = gz_file.read(100)
                        
                        # If we got here, it's valid gzip, decompress the whole thing
                        with gzip.open(downloaded_file, 'rt', encoding='utf-8') as gz_file:
                            with open(final_file, 'w', encoding='utf-8') as out_file:
                                out_file.write(gz_file.read())
                        
                        # Remove compressed file after successful decompression
                        downloaded_file.unlink()
                        
                        final_size = final_file.stat().st_size
                        print(f"  ✓ Decompressed to {final_file.name} ({final_size / 1024 / 1024:.1f} MB)")
                        
                    except (gzip.BadGzipFile, UnicodeDecodeError, OSError) as e:
                        # Not actually compressed, rename file
                        print(f"  → File not actually compressed, renaming to .json")
                        if downloaded_file.exists():
                            downloaded_file.rename(dataset_path / f"{filename}.json")
                
                # Double-check: if file looks like it should be compressed but isn't named .gz
                elif not is_compressed and downloaded_file.name.endswith('.json'):
                    # Test if the file is actually gzipped despite headers
                    try:
                        with gzip.open(downloaded_file, 'rt', encoding='utf-8') as gz_file:
                            test_chunk = gz_file.read(100)
                        
                        # It is compressed! Rename and decompress
                        print(f"  → File is actually compressed, fixing...")
                        compressed_file = dataset_path / f"{filename}.json.gz"
                        downloaded_file.rename(compressed_file)
                        
                        with gzip.open(compressed_file, 'rt', encoding='utf-8') as gz_file:
                            with open(final_file, 'w', encoding='utf-8') as out_file:
                                out_file.write(gz_file.read())
                        
                        compressed_file.unlink()
                        final_size = final_file.stat().st_size
                        print(f"  ✓ Decompressed to {final_file.name} ({final_size / 1024 / 1024:.1f} MB)")
                        
                    except (gzip.BadGzipFile, UnicodeDecodeError, OSError):
                        # Actually not compressed, leave as is
                        pass
                
            except requests.RequestException as e:
                print(f"  ✗ Failed to download file {i}: {e}")
                continue
            except Exception as e:
                print(f"  ✗ Error processing file {i}: {e}")
                continue
            
            # Small delay between downloads to be respectful
            time.sleep(0.5)
        
        # Clean up metadata file
        metadata_file.unlink()
        print(f"Cleaned up {metadata_file.name}")
        
        # Verify we got some files
        downloaded_files = list(dataset_path.glob("*.json")) + list(dataset_path.glob("*.json.gz"))
        if not downloaded_files:
            raise DownloadError("No files were successfully downloaded")
        
        print(f"✓ Download complete! Files saved in {dataset_path}/ as {dataset_name}_1.json, {dataset_name}_2.json, etc.")
        return dataset_path
        
    except requests.RequestException as e:
        raise DownloadError(f"API request failed: {e}")
    except Exception as e:
        raise DownloadError(f"Download failed: {e}")

def download_openalex(dataset_name: str, clean_slate: bool = False) -> Path:
    """
    Download dataset from OpenAlex (placeholder for future implementation)
    
    Args:
        dataset_name: Name of dataset  
        clean_slate: Whether to remove existing data first
        
    Returns:
        Path to downloaded dataset directory
    """
    # TODO: Implement OpenAlex download
    raise NotImplementedError("OpenAlex download not yet implemented")


def download_dataset(source: str, dataset_name: str, clean_slate: bool = False) -> Path:
    """
    Download dataset from specified source
    
    Args:
        source: Data source (semantic_scholar, openalex)  
        dataset_name: Name of dataset to download
        clean_slate: Whether to remove existing data first
        
    Returns:
        Path to downloaded dataset directory
        
    Raises:
        DownloadError: If download fails
        ValueError: If source is unknown
    """
    print(f"Downloading {dataset_name} from {source}")
    
    if source == "semantic_scholar":
        return download_semantic_scholar(dataset_name, clean_slate)
    elif source == "openalex":
        return download_openalex(dataset_name, clean_slate)
    else:
        available_sources = ["semantic_scholar", "openalex"] 
        raise ValueError(f"Unknown source '{source}'. Available: {available_sources}")

def get_dataset_info(dataset_name: str) -> dict:
    """
    Get information about a downloaded dataset
    
    Args:
        dataset_name: Name of dataset
        
    Returns:
        Dictionary with dataset information
    """
    dataset_path = config.get_dataset_path(dataset_name)
    
    if not dataset_path.exists():
        return {"exists": False, "path": str(dataset_path)}
    
    # Count files
    json_files = list(dataset_path.glob("*.json"))
    gz_files = list(dataset_path.glob("*.json.gz"))
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in dataset_path.iterdir() if f.is_file())
    
    return {
        "exists": True,
        "path": str(dataset_path),
        "json_files": len(json_files),
        "compressed_files": len(gz_files), 
        "total_files": len(json_files) + len(gz_files),
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        "sample_files": [f.name for f in (json_files + gz_files)[:5]]
    }

# Convenience functions
def download_papers(clean_slate: bool = False) -> Path:
    """Download papers dataset from Semantic Scholar"""
    return download_semantic_scholar("papers", clean_slate)

def download_authors(clean_slate: bool = False) -> Path:
    """Download authors dataset from Semantic Scholar"""
    return download_semantic_scholar("authors", clean_slate)

def download_venues(clean_slate: bool = False) -> Path:
    """Download publication-venues dataset from Semantic Scholar"""
    return download_semantic_scholar("publication-venues", clean_slate)