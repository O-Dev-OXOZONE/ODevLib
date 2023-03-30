from django.core.exceptions import FieldError

class FieldLookupError(FieldError):
    def __init__(self, model_field, lookup_expr) -> None: ...
