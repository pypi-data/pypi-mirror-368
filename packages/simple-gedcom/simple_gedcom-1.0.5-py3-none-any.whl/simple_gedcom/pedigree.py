
from .parser import GedcomParser
from .elements import Person 
from .people import fill_person
from .utils import save_data_to_csv

def get_pedigree(parser: GedcomParser, person_pointer: str = None, max_generations: int = 10) -> list:
    """Get pedigree starting from a specific person or the first person found"""    
    root_child_elements = parser.get_root_child_elements()
    pedigree_data = {}
    start_person = None
    
    if person_pointer:
        # Find the specific person by pointer
        for element in root_child_elements:
            if isinstance(element, Person) and element.get_pointer() == person_pointer:
                start_person = element
                break
        
        if start_person is None:
            raise ValueError(f"Person with pointer '{person_pointer}' not found")
    else:    
        # Use the first person found (Home Person)
        for element in root_child_elements:
            if isinstance(element, Person):
                start_person = element
                break

    # If we found a person (either specified or first one), build the pedigree
    if start_person is not None:
        # Start with the specified person as HP (Home Person)
        hp_data = fill_person(parser, start_person)
        hp_data['Generation'] = 1
        pedigree_data["HP"] = hp_data
                
        # Recursively build the pedigree
        build_pedigree_recursive(parser, start_person, 1, 1, max_generations, pedigree_data)
    
    # Transform the data (pivot and order)
    pedigree = []
    for position, data in pedigree_data.items():
        # Create a new dict with Position as first field
        row = {'Position': position}
        # Add all other fields from the data
        if isinstance(data, dict):
            row.update(data)
        else:
            # If data is not a dict, store it in a 'Value' column
            row['Value'] = data
        pedigree.append(row)
    
    # Sort by Generation
    if pedigree and 'Generation' in pedigree[0]:
        pedigree.sort(key=lambda x: x.get('Generation', 0))
    
    return pedigree

def build_pedigree_recursive(parser: GedcomParser, person: Person, position_number: int, generation: int, max_generations: int, pedigree: dict):
    """Recursively build pedigree up to max_generations"""
           
    # Stop if we've reached the maximum generation
    if generation > max_generations:
        return
    
    # Get father and mother
    father, mother = parser.get_father_mother(person)
    
    # Calculate positions for next generation (binary tree numbering)
    father_position = position_number * 2
    mother_position = position_number * 2 + 1
        
    father_key = get_position_key(father_position, generation + 1)
    mother_key = get_position_key(mother_position, generation + 1)

    # Process father
    if father is not None:
        father_data = fill_person(parser, father)
        father_data['Generation'] = generation + 1
        pedigree[father_key] = father_data
        build_pedigree_recursive(parser, father, father_position, generation + 1, max_generations, pedigree)
    
    # Process mother
    if mother is not None:
        mother_data = fill_person(parser, mother)
        mother_data['Generation'] = generation + 1
        pedigree[mother_key] = mother_data
        build_pedigree_recursive(parser, mother, mother_position, generation + 1, max_generations, pedigree)

def get_position_key(position_number: int, generation: int) -> str:
    """Generate position key based on generation and position number"""

    if generation == 2:  # Parents
        return "P1" if position_number == 2 else "P2"
    elif generation == 3:  # Grandparents
        return f"GP{position_number - 3}"
    else:  # Great-grandparents and beyond
        g_count = generation - 3
        g_prefix = "G" * g_count
        generation_start = 2 ** (generation - 1) 
        relative_position = position_number - generation_start + 1
        return f"{g_prefix}GP{relative_position}"

def remove_duplicates_from_pedigree(pedigree):
    """Remove duplicate people, keeping only the first occurrence of each person"""
    seen_person_ids = set()
    unique_pedigree = []
    
    for entry in pedigree:
        person_id = entry.get('Person ID')
        if person_id not in seen_person_ids:
            seen_person_ids.add(person_id)
            unique_pedigree.append(entry)
        # Skip if we've already seen this person
    
    return unique_pedigree

def save_pedigree_to_csv(parser: GedcomParser, output_filename: str = None) -> str:
    """Get pedigree data and save to CSV file"""
    # Get the pedigree data
    pedigree_list = get_pedigree(parser)
    return save_data_to_csv(parser, pedigree_list, " pedigree", output_filename)


def show_generation_counts(pedigree):
    """Show count of ancestors in each generation vs maximum possible"""
    from collections import Counter
    
    # Count people per generation
    generation_counts = Counter(entry.get('Generation') for entry in pedigree)
    
    print("Generation Analysis:")
    print("Gen | Actual | Max Possible | Percentage | Description")
    print("----|--------|--------------|------------|------------------")
    
    total_actual = 0
    total_possible = 0
    
    # Get all generations present
    generations = sorted(generation_counts.keys())
    
    for gen in generations:
        actual = generation_counts[gen]
        max_possible = 2 ** (gen - 1)  # 2^(generation-1)
        percentage = (actual / max_possible) * 100 if max_possible > 0 else 0
        
        # Description
        if gen == 1:
            desc = "Home Person"
        elif gen == 2:
            desc = "Parents"
        elif gen == 3:
            desc = "Grandparents"
        elif gen == 4:
            desc = "Great-grandparents"
        elif gen == 5:
            desc = "2nd great-grandparents"
        elif gen == 6:
            desc = "3rd great-grandparents"
        elif gen == 7:
            desc = "4th great-grandparents"
        elif gen == 8:
            desc = "5th great-grandparents"
        elif gen == 9:
            desc = "6th great-grandparents"
        elif gen == 10:
            desc = "7th great-grandparents"
        elif gen == 11:
            desc = "8th great-grandparents"
        else:
            # For generations beyond 11
            ordinal = gen - 3
            desc = f"{ordinal}th great-grandparents"

        print(f" {gen:2d} | {actual:6d} | {max_possible:12d} | {percentage:8.1f}% | {desc}")
        
        total_actual += actual
        total_possible += max_possible
    
    overall_percentage = (total_actual / total_possible) * 100 if total_possible > 0 else 0
    
    print("----|--------|--------------|------------|------------------")
    print(f"Tot | {total_actual:6d} | {total_possible:12d} | {overall_percentage:8.1f}% | Overall completeness")
    
def show_pedigree_duplicates(pedigree):
    """Show duplicate analysis for pedigree entries"""
    from collections import Counter
    
    person_ids = [entry.get('Person ID') for entry in pedigree]
    id_counts = Counter(person_ids)

    unique_people = len(id_counts)
    total_entries = len(pedigree)
    duplicate_entries = total_entries - unique_people

    print(f"Total entries: {total_entries}")
    print(f"Unique people: {unique_people}")
    print(f"Duplicate entries: {duplicate_entries}")

    # Show people with multiple appearances including generation info
    multiple_appearances = {pid: count for pid, count in id_counts.items() if count > 1}
    print(f"\nPeople appearing multiple times: {len(multiple_appearances)}")

    for pid, count in multiple_appearances.items():
        # Find all entries for this person
        person_entries = [entry for entry in pedigree if entry.get('Person ID') == pid]
        first_entry = person_entries[0]
        name = f"{first_entry.get('First Name', '')} {first_entry.get('Last Name', '')}"
        generations = [entry.get('Generation') for entry in person_entries]
        positions = [entry.get('Position') for entry in person_entries]
        
        print(f"  {name} ({pid}): {count} times")
        
        unique_generations = list(set(generations))
        if len(unique_generations) == 1:
            print(f"    Generation: {unique_generations[0]} ({count} times)")
        else:
            print(f"    Generations: {generations}")
            
        print(f"    Positions: {positions}")