from collections.abc import Callable
from typing import TypeVar

O = TypeVar('O')  # noqa: E741
N = TypeVar('N')


def diff(old_list: list[O], new_list: list[N], comparator: Callable[[O, N], bool]) -> tuple[list[O], list[N]]:
    """
    Compare old and new element lists and tells which elements to create and which to delete to get new list from the
    old one. For elements to delete the function returns elements from the old_list, for elements to create — elements
    from the new_list.

    @param old_list: old list, from which we want to get the new list.
    @param new_list: new list, which we want to get from the old list.
    @param comparator function that receives two elements and returns if they are equal.
    @return tuple (elements_to_delete, elements_to_create).

    Example: diff([1, 2], [2, 3]) == ([1], [3]).
    """

    # Create copies to leave input arguments unmodified
    _old_list = old_list[:]
    _new_list = new_list[:]

    for o in old_list:
        for n in new_list:
            if comparator(o, n):
                _old_list.remove(o)
                break

    for n in new_list:
        for o in old_list:
            if comparator(o, n):
                _new_list.remove(n)
                break

    return _old_list, _new_list  # (to_delete, to_create)
