"""
Contains various functional programming utilities.
"""

from typing import Iterable, List, TypeVar, Optional


T = TypeVar("T")
""" Generic type variable for use in type annotations. """


def flatten(list_of_lists: Iterable[Iterable[T]]) -> List[T]:
    """
    Extracts nested lists of elements into a single list of elements.

    Example:

    .. code-block:: python

       flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]
    """
    return [element for sublist in list_of_lists for element in sublist]


def first(iterable: Iterable[T]) -> Optional[T]:
    """
    Returns the first element of an iterable.

    Example:
    
    .. code-block:: python

       first([1, 2, 3]) == 1
    """
    return next(iterable.__iter__(), None)
