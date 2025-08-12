from typing import List
from .parser import GedcomParser
from .people import fill_person
from .pedigree import get_pedigree, remove_duplicates_from_pedigree
from .utils import save_data_to_csv

def get_source_list(parser: GedcomParser) -> List[dict]:
    """Get all source records as dictionaries"""
    sources_dict = parser.get_sources()
    
    sources_list = []
    for source in sources_dict.values():
        source_data = {
            'Source ID': source.get_pointer(),
            'Title': source.get_title(),
            'Author': source.get_author(),
            'Publication': source.get_publication(),
            'Repository': source.get_repository()
        }
        sources_list.append(source_data)
    
    return sources_list

def get_person_source_list(parser: GedcomParser) -> List[dict]:
    """Get people data with one row per person-source combination"""
    person_source_list = []

    # Go through all individuals
    for person in parser.get_individuals().values():

        person_data = fill_person(GedcomParser, person)

        person_sources = person.get_all_person_sources()

        if person_sources:
            # Create one row per source
            for source_pointer in person_sources:
                sources_dict = parser.get_sources()
                if source_pointer in sources_dict:
                    source = sources_dict[source_pointer]

                    # pick the appropriate fields
                    row_data = {
                        'First Name': person_data.get('First Name'),
                        'Last Name': person_data.get('Last Name'),
                        'Birth Date': person_data.get('Birth Date'),
                        'Birth Place': person_data.get('Birth Place'),
                        'Death Date': person_data.get('Death Date'),
                        'Death Place': person_data.get('Death Place'),
                        'Source Title': source.get_title(),
                        'Source Publication': source.get_publication(),
                        'Person ID': person_data.get('Person ID') 
                    }

                    person_source_list.append(row_data)

        else:
            # Person has no sources - include them with empty source fields
            row_data = {
                'First Name': person_data.get('First Name'),
                'Last Name': person_data.get('Last Name'),
                'Birth Date': person_data.get('Birth Date'),
                'Birth Place': person_data.get('Birth Place'),
                'Death Date': person_data.get('Death Date'),
                'Death Place': person_data.get('Death Place'),
                'Source Title': '',
                'Source Publication': '',
                'Person ID': person_data.get('Person ID') 
            }

            person_source_list.append(row_data)
            
    return person_source_list


def get_pedigree_source_list(parser: GedcomParser) -> List[dict]:
    """Get pedigree data with one row per person-source combination"""
    pedigree_source_list = []

    # Get the pedigree data
    pedigree = get_pedigree(parser)
    pedigree = remove_duplicates_from_pedigree(pedigree)
    
    # Get all individuals once
    individuals = parser.get_individuals()

        # Go through each person in the pedigree
    for pedigree_person in pedigree:
        person_id = pedigree_person.get('Person ID')
                    
        person = individuals[person_id]
        
        # Pedigree person data
        pedigree_data = {
            'Position': pedigree_person.get('Position'),
            'Generation': pedigree_person.get('Generation'),
            'First Name': pedigree_person.get('First Name'),
            'Last Name': pedigree_person.get('Last Name'),
            'Birth Date': pedigree_person.get('Birth Date'),
            'Birth Place': pedigree_person.get('Birth Place'),
            'Death Date': pedigree_person.get('Death Date'),
            'Death Place': pedigree_person.get('Death Place')
        }

        # Get all sources for this person
        person_sources = person.get_all_person_sources()

        if person_sources:
            # Create one row per source
            for source_pointer in person_sources:
                sources_dict = parser.get_sources()
                if source_pointer in sources_dict:

                    source = sources_dict[source_pointer]

                    row_data = pedigree_data.copy()
                    
                    row_data.update({
                        'Source Title': source.get_title(),
                        'Source Publication': source.get_publication(),
                        'Person ID': person_id
                    })

                    pedigree_source_list.append(row_data)
        else:
            # If no sources, add the person data without source information
            row_data = pedigree_data.copy()
            row_data.update({
                'Source Title': '',
                'Source Publication': '',
                'Person ID': person_id
            })
            pedigree_source_list.append(row_data)

    return pedigree_source_list

def save_source_list_to_csv(parser: GedcomParser, output_filename: str = None) -> str:
    """Get source data and save to CSV file"""
    sources = get_source_list(parser)
    return save_data_to_csv(parser, sources, " sources", output_filename)

def save_person_source_list_to_csv(parser: GedcomParser, output_filename: str = None) -> str:
    """Get person source data and save to CSV file"""
    person_source_list = get_person_source_list(parser)
    return save_data_to_csv(parser, person_source_list, " people sources", output_filename)

def save_pedigree_source_list_to_csv(parser: GedcomParser, output_filename: str = None) -> str:
    """Get pedigree source data and save to CSV file"""
    pedigree_source_list = get_pedigree_source_list(parser)
    return save_data_to_csv(parser, pedigree_source_list, " pedigree sources", output_filename)