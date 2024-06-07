from dataclasses import dataclass
from typing import List, Tuple


class WordDict:
    """
    Data structure to store a language thesaurus.

    It is a wrapper around a dictionary. The main
    function of this type is to tag dictionaries that
    represent the structure of WordDict.

    Each key represents a category. Each category has
    a list of categories or a list of words.
    {
        'root':
        {
            'A':
            {
                'words': [...]
            }
            ,
            'B':
            {

            }
        }
    }
    """

    def __init__(self, source_data):
        self._data = source_data

    def __getitem__(self, key):
        return WordDict(self._data[key])

    def __setitem__(self, key, value):
        self._data[key] = value

    def __str__(self):
        return self._data.__str__()

    def extract(self):
        return self._data


@dataclass
class ReplaceInstructions:
    key: List[str]
    replace_pairs: List[Tuple[str]]
