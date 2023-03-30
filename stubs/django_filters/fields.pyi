from .conf import settings as settings
from .constants import EMPTY_VALUES as EMPTY_VALUES
from .utils import handle_timezone as handle_timezone
from .widgets import BaseCSVWidget as BaseCSVWidget, CSVWidget as CSVWidget, DateRangeWidget as DateRangeWidget, LookupChoiceWidget as LookupChoiceWidget, RangeWidget as RangeWidget
from _typeshed import Incomplete
from django import forms

class RangeField(forms.MultiValueField):
    widget: Incomplete
    def __init__(self, fields: Incomplete | None = ..., *args, **kwargs) -> None: ...
    def compress(self, data_list): ...

class DateRangeField(RangeField):
    widget: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def compress(self, data_list): ...

class DateTimeRangeField(RangeField):
    widget: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class IsoDateTimeRangeField(RangeField):
    widget: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class TimeRangeField(RangeField):
    widget: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class Lookup:
    def __new__(cls, value, lookup_expr): ...

class LookupChoiceField(forms.MultiValueField):
    default_error_messages: Incomplete
    def __init__(self, field, lookup_choices, *args, **kwargs) -> None: ...
    def compress(self, data_list): ...

class IsoDateTimeField(forms.DateTimeField):
    ISO_8601: str
    input_formats: Incomplete
    def strptime(self, value, format): ...

class BaseCSVField(forms.Field):
    base_widget_class: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def clean(self, value): ...

class BaseRangeField(BaseCSVField):
    widget: Incomplete
    default_error_messages: Incomplete
    def clean(self, value): ...

class ChoiceIterator:
    field: Incomplete
    choices: Incomplete
    def __init__(self, field, choices) -> None: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class ModelChoiceIterator(forms.models.ModelChoiceIterator):
    def __iter__(self): ...
    def __len__(self) -> int: ...

class ChoiceIteratorMixin:
    null_label: Incomplete
    null_value: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    choices: Incomplete

class ChoiceField(ChoiceIteratorMixin, forms.ChoiceField):
    iterator: Incomplete
    empty_label: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class MultipleChoiceField(ChoiceIteratorMixin, forms.MultipleChoiceField):
    iterator: Incomplete
    empty_label: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class ModelChoiceField(ChoiceIteratorMixin, forms.ModelChoiceField):
    iterator: Incomplete
    def to_python(self, value): ...

class ModelMultipleChoiceField(ChoiceIteratorMixin, forms.ModelMultipleChoiceField):
    iterator: Incomplete
