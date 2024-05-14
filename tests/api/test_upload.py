import pytest
from kitty import Text

def test_upload(mock_cat_db):
    text = Text(id="test", inst_id="test", text="test", catalog_id="test", 
            pdf_id="test", png_id="test", conversion="test", page="test", 
            annotated=False)

    doc_id = mock_cat_db.upload(text)
    assert doc_id is not None