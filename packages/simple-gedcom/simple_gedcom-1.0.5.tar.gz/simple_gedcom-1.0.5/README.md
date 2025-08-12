# Simple GEDCOM Parser

A simplified Python library for extracting genealogy data from GEDCOM files:

1. **Extract basic person data** - Get a list of people with vital information
2. **Extract sources** - Get lists of documentary sources
3. **Extract pedigree** - Get direct ancestors

## Features

- Parse GEDCOM 5.5 files
- Extract person data: names, birth/death dates and places, parents
- Extract source citations linked to individuals
- Extract pedigree
- Simple, clean API designed for data analysis and writing to csv files

## Quick Start

```python

# Read a GEDCOM file and write lists to CSV files
from simple_gedcom import load_gedcom

gedcom = load_gedcom('data/tree.ged')

gedcom.save_person_list_to_csv()

gedcom.save_pedigree_to_csv()

gedcom.save_source_list_to_csv()

gedcom.save_person_source_list_to_csv()

# pedigree analytics
pedigree = gedcom.get_pedigree()

gedcom.show_generation_counts(pedigree) 

gedcom.show_pedigree_duplicates(pedigree) 

# Use pandas to display lists
import pandas as pd

person_list = gedcom.get_person_list()
df_person_list = pd.DataFrame(person_list)
print(df_person_list.head())

sources = gedcom.get_source_list()
df_sources = pd.DataFrame(sources)
print(df_sources.head()) 

person_sources = gedcom.get_person_source_list()
df_person_sources = pd.DataFrame(person_sources)
print(df_person_sources.head())

pedigree = gedcom.get_pedigree()
df_pedigree = pd.DataFrame(pedigree)
print(df_pedigree.head())

# Search by name
found = gedcom.find_persons_by_name(first_name="Theodore")
df_found = pd.DataFrame(found)
print(df_found.head())

# Show the pedigree for a specific person (by ID)
pedigree = gedcom.get_pedigree("@I162694122750@")
df_pedigree = pd.DataFrame(pedigree)
print(df_pedigree.head())

```

## Requirements

- Python 3.6+
- No external dependencies for core functionality
- pandas (optional, for DataFrame examples)

## License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

## Attribution

This project is derived from [python-gedcom](https://github.com/nickreynke/python-gedcom) by Nicklas Reincke and contributors. The original project provided the foundation for GEDCOM parsing, which has been simplified and focused for specific genealogy data extraction use cases.

Original Copyright (C) 2018-2019 Nicklas Reincke and contributors  
Simplified version Copyright (C) 2025 [mcobtechnology]

## Contributing

This is a simplified, focused library. If you need additional GEDCOM functionality, consider using the full-featured [python-gedcom](https://github.com/nickreynke/python-gedcom) library.

For bug fixes and improvements to the core functionality, feel free to open issues or submit pull requests.