"""
Configuration management for SciSciDB
Handles HPC vs local environment differences
"""
import os
from pathlib import Path

class Config:
    def __init__(self):
        self._setup_environment()
        self._setup_paths()
        self._setup_database()
        self._setup_api_keys()
    
    def _setup_environment(self):
        """Detect if we're running on HPC or locally"""
        self.is_hpc = os.path.exists('/netfiles') or os.getenv('HPC_ENV', '').lower() == 'true'
        self.environment = 'hpc' if self.is_hpc else 'local'
    
    def _setup_paths(self):
        """Setup data paths based on environment"""
        if self.is_hpc:
            # HPC: Check for custom data path first
            custom_data_path = os.getenv('SCISCI_DATA_PATH')
            if custom_data_path:
                self.data_root = Path(custom_data_path)
            else:
                # Try group and personal directories
                username = os.getenv('USER', 'default_user')
                group_name = os.getenv('SCISCI_GROUP', 'compethicslab')  # Default to compethicslab
                
                potential_paths = [
                    Path(f'/netfiles/{group_name}/scisciDB/semanticscholar'),    # Group data
                    Path(f'/netfiles/{group_name}/scisci_data'),                 # Group alt
                    Path(f'/netfiles/{username}/scisci_data'),                   # Personal
                ]
                
                # Use the first one that exists and has data
                self.data_root = None
                for path in potential_paths:
                    if path.exists():
                        # Check if it has dataset directories or files
                        has_data = (
                            any(path.iterdir()) or 
                            any((path / subdir).exists() for subdir in ['papers', 'authors', 'publication-venues'])
                        )
                        if has_data:
                            self.data_root = path
                            print(f"Using data directory: {path}")
                            break
                
                # Fallback to personal directory
                if not self.data_root:
                    self.data_root = Path(f'/netfiles/{username}/scisci_data')
                    print(f"No existing data found, using: {self.data_root}")
            
            self.temp_dir = Path('/tmp/scisci_temp')
        else:
            # Local: Use project-relative paths
            project_root = Path(__file__).parent.parent  # backend/
            self.data_root = project_root / 'data'
            self.temp_dir = project_root / 'temp'
        
        # Ensure directories exist
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Export directory for static files
        self.export_dir = self.data_root / 'exports'
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_database(self):
        """Setup database connection settings"""
        self.mongo_uri = os.getenv(
            'MONGO_URI', 
            'mongodb://localhost:27017'  # Default for local dev
        )
        self.db_name = os.getenv('DB_NAME', 'papersDB')
    
    def _setup_api_keys(self):
        """Setup API keys for external services"""
        self.semantic_scholar_key = os.getenv('S2_API_KEY')
        
        # Warn if missing (but don't crash)
        if not self.semantic_scholar_key:
            print("Warning: S2_API_KEY not set. Semantic Scholar downloads may be limited.")
    
    def get_dataset_path(self, dataset_name: str) -> Path:
        """Get the path for a specific dataset, handling name variations"""
        base_path = self.data_root / dataset_name
        
        # If exact name exists, use it
        if base_path.exists():
            return base_path
        
        # Handle common name variations
        name_variations = {
            'publication-venues': ['venues', 'publication_venues', 'publicationvenues', 'publication-venues'],
            'venues': ['publication-venues', 'publication_venues', 'publicationvenues'],
            'authors': ['author'],
            'papers': ['paper'],
        }
        
        if dataset_name in name_variations:
            for variation in name_variations[dataset_name]:
                variant_path = self.data_root / variation
                if variant_path.exists():
                    print(f"Found {dataset_name} data at: {variant_path}")
                    return variant_path
        
        # Return original path (might not exist, but that's okay)
        return base_path
    
    def print_config(self):
        """Print current configuration (for debugging)"""
        print(f"Environment: {self.environment}")
        print(f"Data root: {self.data_root}")
        print(f"Export dir: {self.export_dir}")
        print(f"Database: {self.db_name} @ {self.mongo_uri}")
        print(f"S2 API Key: {'✓ Set' if self.semantic_scholar_key else '✗ Missing'}")


    def test_database_connection(self):
        """Test database connection and show detailed error info"""
        print("Testing database connection...")
        try:
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
            
            print(f"Attempting to connect to: {self.db_name} database")
            print(f"Using URI: {self.mongo_uri.split('@')[0]}@***" if '@' in self.mongo_uri else self.mongo_uri)
            
            # Create client with short timeout for testing
            client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            
            # Test connection
            client.admin.command('ping')
            print("✓ Database connection successful!")
            
            # Test database access
            db = client[self.db_name]
            collections = db.list_collection_names()
            print(f"✓ Database '{self.db_name}' accessible")
            print(f"✓ Found {len(collections)} collections: {collections}")
            
            client.close()
            return True
            
        except ConnectionFailure as e:
            print(f"✗ Connection failed: {e}")
            print("  Check if MongoDB server is running and accessible")
            return False
        except ServerSelectionTimeoutError as e:
            print(f"✗ Server selection timeout: {e}")
            print("  Check network connectivity and server address")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False
        
# Singleton instance
config = Config()

# Convenience functions
def get_dataset_path(dataset_name: str) -> Path:
    """Get path for a dataset"""
    return config.get_dataset_path(dataset_name)

def is_hpc() -> bool:
    """Check if running on HPC"""
    return config.is_hpc