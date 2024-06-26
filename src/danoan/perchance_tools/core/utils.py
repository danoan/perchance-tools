from danoan.perchance_tools.core import model

import copy


def collect_key_path(source: model.WordDict, target_key: str):
    """
    Finds all the sequences of dictionary keys leading to some target key.

    >>> d = {
    ...     'root':
    ...     {
    ...         'Category_A':
    ...         {
    ...             'Category_B1':
    ...             {
    ...                 'words':
    ...                 [
    ...                     'word_a',
    ...                     'word_b',
    ...                     'word_c'
    ...                 ]
    ...             },
    ...             'Category_B2':
    ...             {
    ...                 'words':
    ...                 [
    ...                     'word_d',
    ...                     'word_e'
    ...                 ]
    ...             }
    ...         }
    ...     }
    ... }
    >>> w = model.WordDict(d)
    >>> L = list(collect_key_path(w,'words'))
    >>> assert( L[0]['path'] == ['root', 'Category_A', 'Category_B1'] )
    >>> assert( L[0]['words'] == ['word_a', 'word_b', 'word_c'] )
    """

    def __traverse__(T, path):
        assert type(T) is dict

        for key in T.keys():
            if key == target_key:
                yield {"path": path, target_key: T[key]}
            else:
                path.append(key)
                for x in __traverse__(T[key], path):
                    yield x
                path.pop()

    for data_dict in __traverse__(source.extract(), []):
        dict_copy = copy.deepcopy(data_dict)
        yield dict_copy
