from dataclasses import dataclass
from typing import List, Tuple


class WordDict:
    """
    Data structure to store a language thesaurus.

    Each key represents a category. Each category has
    a list of categories or a list of words.
    {
        'root':
        [
            'A':
            [
                {
                    'words': [...]
                }
            ],
            'B':
            [

            ]
        ]
    }
    """

    def __init__(self, base_list):
        self._data = base_list

    def __getitem__(self, key):
        if type(self._data) is list:
            for d in self._data:
                if key in d:
                    return WordDict(d[key])
            raise KeyError(f"key {key} not found.")
        elif type(self._data) is dict:
            return WordDict(self._data[key])

    def __setitem__(self, key, value):
        if type(self._data) is list:
            for d in self._data:
                if key in d:
                    d[key] = value
                    return
        elif type(self._data) is dict:
            self._data[key] = value

    def __str__(self):
        return self._data.__str__()

    def extract(self):
        return self._data


@dataclass
class CorrectionInstructions:
    categories: List[str]
    corrections: List[Tuple[str]]
