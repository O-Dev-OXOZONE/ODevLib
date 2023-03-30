from functools import reduce


def snake_case(s: str) -> str:
    return reduce(lambda x, y: x + ('_' if y.isupper() else '') + y, s).lower()
