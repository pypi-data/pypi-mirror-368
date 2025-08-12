from typing import List
from .parser import GedcomParser

def save_data_to_csv(parser: GedcomParser, data_list: List[dict], suffix: str, output_filename: str = None) -> str:
    """Common function to save data list to CSV file"""
    import csv
    import os
    
    # Get the original GEDCOM file path from parser
    gedcom_filepath = parser.get_file_path()
    if gedcom_filepath is None:
        raise ValueError("No GEDCOM file has been parsed yet")
    
    # If no output filename specified, use the GEDCOM file's path and name
    if output_filename is None:
        directory = os.path.dirname(gedcom_filepath)
        base_name = os.path.splitext(os.path.basename(gedcom_filepath))[0]
        output_filename = os.path.join(directory, f"{base_name}{suffix}.csv")
    
    # Handle empty data
    if not data_list:
        # Create empty CSV file
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            pass
        return output_filename
    
    # Get column headers from the first record
    headers = list(data_list[0].keys())
    
    # Write to CSV
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_list)
    
    return output_filename