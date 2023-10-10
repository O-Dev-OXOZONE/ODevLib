"""
Contains various functional programming utilities.
"""

from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
""" Generic type variable for use in type annotations. """

V = TypeVar("V")
""" Generic type variable for use in type annotations. """


def flatten(list_of_lists: Iterable[Iterable[T]]) -> list[T]:
    """
    Extract nested lists of elements into a single list of elements.

    Example:
    -------
    .. code-block:: python

       flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]
    """
    return [element for sublist in list_of_lists for element in sublist]


def first(iterable: Iterable[T]) -> T | None:
    """
    Return the first element of an iterable.

    Example:
    -------
    .. code-block:: python

       first([1, 2, 3]) == 1
    """
    return next(iterable.__iter__(), None)


def lazy_filter(check: Callable[[T], bool], iterable: Iterable[Callable[[], T]]) -> Iterable[T]:
    for x in iterable:
        if check(val := x()):
            yield val


def lazy_not_nullable_first(iterable: Iterable[Callable[[], T]]) -> T | None:
    return first(lazy_filter(lambda x: x is not None, iterable))


def filter_non_null(iterable: Iterable[T | None]) -> Iterable[T]:
    """
    Filter out null values from an iterable.

    Example:
    -------
    .. code-block:: python

       filter_non_null([1, None, 2, None, 3]) == [1, 2, 3]
    """
    for it in iterable:
        if it is not None:
            yield it


def group_by(it: Iterable[T], field_extractor: Callable[[T], V]) -> Iterable[tuple[V, list[T]]]:
    """
    Group elements of an iterable by a given field.

    @param it: iterable to process
    @param field_extractor: function to extract a field from an element of the iterable
    @return: iterable of tuples (field_value, list_of_elements_with_this_field_value)
    """
    result = defaultdict(list)
    for item in it:
        key = field_extractor(item)
        result[key].append(item)
    return list(result.items())


def until(value: T, it: Iterable[T]) -> Iterable[T]:
    """
    Return all values of an iterable until the specified value is reached.
    May be used to only get new values when overlapping getters are used.

    @param value: value to stop at
    @param it: iterable to process
    @return: iterable of values until the specified value is reached. The specified value is not included.
    """
    for i in it:
        if i == value:
            return
        yield i


def until_f(value: T, it: Iterable[V], f: Callable[[T, V], bool]) -> Iterable[V]:
    """
    Return all values of an iterable until the specified value is reached.
    May be used to only get new values when overlapping getters are used.
    Uses f instead of "==" to compare values. As soon as True is obtained, aborts the iterable.

    @param value: value to stop at
    @param it: iterable to process
    @param f: callable that is used to compare values. First argument is "value", second is the current iterable value.
    @return: iterable of values until the specified value is reached. The specified value is not included.
    """
    for i in it:
        if f(value, i):
            return
        yield i
