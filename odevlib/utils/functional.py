from typing import Iterable, List, TypeVar, Optional

T = TypeVar('T')


def flatten(list_of_lists: Iterable[Iterable[T]]) -> List[T]:
    """
    Extracts nested lists of elements into a single list of elements.

    Example: flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4].
    """
    return [element for sublist in list_of_lists for element in sublist]


def first(iterable: Iterable[T]) -> Optional[T]:
    return next(iterable.__iter__(), None)
