# tests/test_simple_gedcom.py
import pytest
import os
import tempfile
from simple_gedcom import load_gedcom

def test_load_gedcom():
    """Test that we can load the sample GEDCOM file"""
    gedcom = load_gedcom('tests/data/tree.ged')
    assert gedcom is not None

def test_load_nonexistent_file():
    """Test error handling for missing files"""
    with pytest.raises(FileNotFoundError):
        load_gedcom('does_not_exist.ged')

def test_csv_exports():
    """Test all CSV export functions work without errors"""
    gedcom = load_gedcom('tests/data/tree.ged')
    
    # simple tests that the functions do not crash
    gedcom.save_person_list_to_csv()
    gedcom.save_pedigree_to_csv()
    gedcom.save_source_list_to_csv()
    gedcom.save_person_source_list_to_csv()