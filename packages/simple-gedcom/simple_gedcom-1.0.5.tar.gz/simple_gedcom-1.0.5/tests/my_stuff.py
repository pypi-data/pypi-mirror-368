from simple_gedcom import load_gedcom
import pandas as pd

gedcom = load_gedcom('data/Sharon Richards Family Tree.ged')

"""
gedcom.save_person_list_to_csv()

gedcom.save_pedigree_to_csv()

gedcom.save_source_list_to_csv()

gedcom.save_person_source_list_to_csv()

# pedigree analytics
pedigree = gedcom.get_pedigree()

gedcom.show_generation_counts(pedigree) 

gedcom.show_pedigree_duplicates(pedigree) 

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
"""

# Show the pedigree for a specific person (by ID)
pedigree = gedcom.get_pedigree("@I75022034717@")
df_pedigree = pd.DataFrame(pedigree)
print(df_pedigree.head())

"""
gedcom.save_person_list_to_csv()

gedcom.save_pedigree_to_csv()

gedcom.save_source_list_to_csv()

gedcom.save_person_source_list_to_csv()

gedcom.save_pedigree_source_list_to_csv()


person_list = gedcom.get_person_list()
df_person_list = pd.DataFrame(person_list)
print("PERSON LIST")
print(df_person_list.head())

sources = gedcom.get_source_list()
df_sources = pd.DataFrame(sources)
print("")
print("SOURCE LIST")
print(df_sources.head()) 

person_sources = gedcom.get_person_source_list()
df_person_sources = pd.DataFrame(person_sources)
print("")
print("PERSON SOURCES")
print(df_person_sources.head())

pedigree = gedcom.get_pedigree()
df_pedigree = pd.DataFrame(pedigree)
print("")
print("PEDIGREE")
print(df_pedigree.head())

found = gedcom.find_persons_by_name(first_name="John")
df_found = pd.DataFrame(found)
print(df_found.head())

pedigree = gedcom.get_pedigree("@I75022061467@")
df_pedigree = pd.DataFrame(pedigree)
print("")
print("PEDIGREE")
print(df_pedigree.head())

pedigree_source_list = gedcom.get_pedigree_source_list()
df_pedigree_source_list = pd.DataFrame(pedigree_source_list)
print("")
print("PEDIGREE SOURCE LIST")
print(df_pedigree_source_list.head())

gedcom.save_pedigree_to_csv()

gedcom.save_pedigree_source_list_to_csv()

# for item in pedigree: print(item['Position'])
# print(f"Pedigree list count: {len(pedigree)}")

gedcom.save_pedigree_source_list_to_csv()


pedigree = gedcom.get_pedigree()

gedcom.show_generation_counts(pedigree) 

gedcom.show_pedigree_duplicates(pedigree) 


# use pandas
import pandas as pd
pd.set_option('display.max_colwidth', 50)
pd.set_option('display.max_columns', None)

pedigree = gedcom.get_pedigree()

df_pedigree = pd.DataFrame(pedigree)
print("")
print("PEDIGREE")
print(df_pedigree[['Position', 'First Name', 'Last Name']].head(20))
"""
