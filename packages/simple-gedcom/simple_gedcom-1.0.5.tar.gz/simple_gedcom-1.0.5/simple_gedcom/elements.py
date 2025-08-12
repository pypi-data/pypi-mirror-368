from typing import List, Tuple

class GedcomElement:
    """Base class for GEDCOM elements"""

    def __init__(self, level: int, pointer: str, tag: str, value: str):
        self.__level = level
        self.__pointer = pointer
        self.__tag = tag
        self.__value = value
        self.__children = []

    def get_level(self) -> int:
        return self.__level

    def get_pointer(self) -> str:
        return self.__pointer

    def get_tag(self) -> str:
        return self.__tag

    def get_value(self) -> str:
        return self.__value

    def get_children(self) -> List['GedcomElement']:
        return self.__children

    def add_child(self, element: 'GedcomElement'):
        self.__children.append(element)

    def get_child_elements(self, tag: str = None) -> List['GedcomElement']:
        if tag is None:
            return self.__children
        return [child for child in self.__children if child.get_tag() == tag]

    def get_child_value(self, tag: str) -> str:
        """Value of the first child element with a specific tag"""
        elements = self.get_child_elements(tag)
        return elements[0].get_value() if elements else ''


class Person(GedcomElement):
    """Individual person element"""

    def get_name(self) -> Tuple[str, str]:
        """Returns (first_name, last_name)"""
        name_elements = self.get_child_elements('NAME')
        if not name_elements:
            return ('', '')

        name_value = name_elements[0].get_value()
        if not name_value:
            return ('', '')

        # Handle GEDCOM name format: "John /Doe/"
        if '/' in name_value:
            parts = name_value.split('/')
            given_names = parts[0].strip()
            surname = parts[1].strip() if len(parts) > 1 else ''
            return (given_names, surname)
        else:
            # No surname markers
            parts = name_value.strip().split()
            if len(parts) > 1:
                return (' '.join(parts[:-1]), parts[-1])
            elif len(parts) == 1:
                return (parts[0], '')

        return ('', '')

    def get_gender(self) -> str:
        return self.get_child_value('SEX')

    def get_birth_date_place(self) -> Tuple[str, str]:
        birth_elements = self.get_child_elements('BIRT')
        if not birth_elements:
            return ('', '')
        birth_element = birth_elements[0]
        birth_date = birth_element.get_child_value('DATE')
        birth_place = birth_element.get_child_value('PLAC')
        return (birth_date, birth_place)

    def get_death_date_place(self) -> Tuple[str, str]:
        death_elements = self.get_child_elements('DEAT')
        if not death_elements:
            return ('', '')
        death_element = death_elements[0]
        death_date = death_element.get_child_value('DATE')
        death_place = death_element.get_child_value('PLAC')
        return (death_date, death_place)

    def get_all_person_sources(self) -> List[str]:
        """Get all source pointers associated with this person"""
        sources = []

        def collect_sources_from_element(element):
            """Recursively collect source pointers from an element and its children"""
            # Get direct sources on this element
            source_elements = element.get_child_elements('SOUR')
            for source_elem in source_elements:
                source_value = source_elem.get_value()
                if source_value:
                    sources.append(source_value)

            # Recursively check all child elements
            for child in element.get_children():
                collect_sources_from_element(child)

        # Collect sources from this person and all their sub-elements
        collect_sources_from_element(self)

        # Remove duplicates and return
        return list(set(sources))


class SourceElement(GedcomElement):
    """Source element"""

    def get_title(self) -> str:
        return self.get_child_value('TITL')

    def get_author(self) -> str:
        return self.get_child_value('AUTH')

    def get_publication(self) -> str:
        return self.get_child_value('PUBL')

    def get_repository(self) -> str:
        return self.get_child_value('REPO')


class FamilyElement(GedcomElement):
    """Family element - minimal implementation for parent lookup"""

    def get_husband(self) -> str:
        return self.get_child_value('HUSB')

    def get_wife(self) -> str:
        return self.get_child_value('WIFE')

    def get_children(self) -> List[str]:
        return [child.get_value() for child in self.get_child_elements('CHIL')]
