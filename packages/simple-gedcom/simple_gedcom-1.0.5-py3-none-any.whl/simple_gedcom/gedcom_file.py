from typing import List
from .parser import GedcomParser
from .people import get_person_list, find_persons_by_name, save_person_list_to_csv
from .pedigree import get_pedigree, save_pedigree_to_csv
from .pedigree import show_generation_counts, show_pedigree_duplicates
from .sources import get_source_list, get_person_source_list, get_pedigree_source_list
from .sources import save_source_list_to_csv, save_person_source_list_to_csv, save_pedigree_source_list_to_csv

class GedcomFile:
    """Wrapper class for GEDCOM file operations"""
    
    def __init__(self, file_path: str):
        self._parser = GedcomParser()
        self._parser.parse_file(file_path)
    
    def get_person_list(self) -> List[dict]:
        return get_person_list(self._parser)
    
    def find_persons_by_name(self, first_name: str = None, last_name: str = None) -> list:
        return find_persons_by_name(self._parser, first_name, last_name)

    def save_person_list_to_csv(self, output_filename: str = None):
        return save_person_list_to_csv(self._parser, output_filename)
    
    def get_source_list(self) -> List[dict]:
        return get_source_list(self._parser)
    
    def save_source_list_to_csv(self, output_filename: str = None):
        return save_source_list_to_csv(self._parser, output_filename)

    def save_person_source_list_to_csv(self, output_filename: str = None):
        return save_person_source_list_to_csv(self._parser, output_filename)

    def get_person_source_list(self) -> List[dict]:
        return get_person_source_list(self._parser)
    
    def get_pedigree(self, person_pointer: str = None) -> List[dict]:
        return get_pedigree(self._parser, person_pointer)

    def show_generation_counts(self, pedigree):
        return show_generation_counts(pedigree)

    def show_pedigree_duplicates(self, pedigree):
        return show_pedigree_duplicates(pedigree)

    def save_pedigree_to_csv(self, output_filename: str = None):
        return save_pedigree_to_csv(self._parser, output_filename)
    
    def get_pedigree_source_list(self) -> List[dict]:
        return get_pedigree_source_list(self._parser)

    def save_pedigree_source_list_to_csv(self, output_filename: str = None):
        return save_pedigree_source_list_to_csv(self._parser, output_filename)

def load_gedcom(file_path: str) -> GedcomFile:
    """Load a GEDCOM file for analysis"""
    return GedcomFile(file_path)

