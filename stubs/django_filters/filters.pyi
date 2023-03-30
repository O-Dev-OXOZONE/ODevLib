from _typeshed import Incomplete

class Filter:
    creation_counter: int
    field_class: Incomplete
    field_name: Incomplete
    lookup_expr: Incomplete
    distinct: Incomplete
    exclude: Incomplete
    extra: Incomplete
    def __init__(self, field_name: Incomplete | None = ..., lookup_expr: Incomplete | None = ..., *, label: Incomplete | None = ..., method: Incomplete | None = ..., distinct: bool = ..., exclude: bool = ..., **kwargs) -> None: ...
    def get_method(self, qs): ...
    def method(self): ...
    def label(self): ...
    @property
    def field(self): ...
    def filter(self, qs, value): ...

class CharFilter(Filter):
    field_class: Incomplete

class BooleanFilter(Filter):
    field_class: Incomplete

class ChoiceFilter(Filter):
    field_class: Incomplete
    null_value: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def filter(self, qs, value): ...

class TypedChoiceFilter(Filter):
    field_class: Incomplete

class UUIDFilter(Filter):
    field_class: Incomplete

class MultipleChoiceFilter(Filter):
    field_class: Incomplete
    always_filter: bool
    conjoined: Incomplete
    null_value: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def is_noop(self, qs, value): ...
    def filter(self, qs, value): ...
    def get_filter_predicate(self, v): ...

class TypedMultipleChoiceFilter(MultipleChoiceFilter):
    field_class: Incomplete

class DateFilter(Filter):
    field_class: Incomplete

class DateTimeFilter(Filter):
    field_class: Incomplete

class IsoDateTimeFilter(DateTimeFilter):
    field_class: Incomplete

class TimeFilter(Filter):
    field_class: Incomplete

class DurationFilter(Filter):
    field_class: Incomplete

class QuerySetRequestMixin:
    queryset: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def get_request(self): ...
    def get_queryset(self, request): ...
    @property
    def field(self): ...

class ModelChoiceFilter(QuerySetRequestMixin, ChoiceFilter):
    field_class: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class ModelMultipleChoiceFilter(QuerySetRequestMixin, MultipleChoiceFilter):
    field_class: Incomplete

class NumberFilter(Filter):
    field_class: Incomplete
    def get_max_validator(self): ...
    @property
    def field(self): ...

class NumericRangeFilter(Filter):
    field_class: Incomplete
    lookup_expr: str
    def filter(self, qs, value): ...

class RangeFilter(Filter):
    field_class: Incomplete
    lookup_expr: str
    def filter(self, qs, value): ...

class DateRangeFilter(ChoiceFilter):
    choices: Incomplete
    filters: Incomplete
    def __init__(self, choices: Incomplete | None = ..., filters: Incomplete | None = ..., *args, **kwargs) -> None: ...
    def filter(self, qs, value): ...

class DateFromToRangeFilter(RangeFilter):
    field_class: Incomplete

class DateTimeFromToRangeFilter(RangeFilter):
    field_class: Incomplete

class IsoDateTimeFromToRangeFilter(RangeFilter):
    field_class: Incomplete

class TimeRangeFilter(RangeFilter):
    field_class: Incomplete

class AllValuesFilter(ChoiceFilter):
    @property
    def field(self): ...

class AllValuesMultipleFilter(MultipleChoiceFilter):
    @property
    def field(self): ...

class BaseCSVFilter(Filter):
    base_field_class: Incomplete
    field_class: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class BaseInFilter(BaseCSVFilter):
    def __init__(self, *args, **kwargs) -> None: ...

class BaseRangeFilter(BaseCSVFilter):
    base_field_class: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class LookupChoiceFilter(Filter):
    field_class: Incomplete
    outer_class: Incomplete
    empty_label: Incomplete
    lookup_choices: Incomplete
    def __init__(self, field_name: Incomplete | None = ..., lookup_choices: Incomplete | None = ..., field_class: Incomplete | None = ..., **kwargs) -> None: ...
    @classmethod
    def normalize_lookup(cls, lookup): ...
    def get_lookup_choices(self): ...
    @property
    def field(self): ...
    lookup_expr: Incomplete
    def filter(self, qs, lookup): ...

class OrderingFilter(BaseCSVFilter, ChoiceFilter):
    descending_fmt: Incomplete
    param_map: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def get_ordering_value(self, param): ...
    def filter(self, qs, value): ...
    @classmethod
    def normalize_fields(cls, fields): ...
    def build_choices(self, fields, labels): ...

class FilterMethod:
    f: Incomplete
    def __init__(self, filter_instance) -> None: ...
    def __call__(self, qs, value): ...
    @property
    def method(self): ...
