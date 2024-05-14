import kitty
import pytest
from pymongo  import MongoClient
import os
import kitty
import mongomock
from kitty import Text, Catalog  # Adjust the import path as necessary

### MOCK LIBRARY FOR BASIC TESTING

@pytest.fixture
def mock_cat_db():
    mock_client = mongomock.MongoClient()
    cat_db_instance = kitty.catDB(mock_client)
    return cat_db_instance

@pytest.fixture(scope="function")
def mock_cat_db_with_items(mock_cat_db):
    """catDB with 3 predefined Catalogs"""
    for i in range(10):
        cc = Catalog(id=f"test_{i}", inst_id="0155zta11", start_year=2020,
                     end_year=2021, cat_type="test", semester=None, college=None)
        mock_cat_db.upload(cc)
        if i < 5:
            converter = 'fitz' if i % 2 == 0 else 'paddleOCR'
            text = Text(id=f"test_{i}_{i}_{converter}", pdf_id=f"test_{i}", png_id=f"test_{i}_{i}", 
                        inst_id="0155zta11", text="test", catalog_id="test",
                        page="test", conversion=converter, annotated=False)
            mock_cat_db.upload(text)

    return mock_cat_db


### REAL LIBRARY TO TEST DATA INTEGRITY

@pytest.fixture(scope="session")
def session_cat_db():
    """kitty"""
    db_ = kitty.catDB()
    yield db_


@pytest.fixture(scope="function")
def cat_db(session_cat_db):
    """Current CardsDB"""
    db = session_cat_db
    return db

# Fetch RORs from the database
cat_db = kitty.catDB()
count_inst = cat_db.count(by="inst_id", collection="cc_catalog")
rors = list(count_inst.keys())  # Your list of RORs

# Define a fixture that will be parameterized with the RORs list
@pytest.fixture(params=rors, scope="session")
def ror(request):
    return request.param

