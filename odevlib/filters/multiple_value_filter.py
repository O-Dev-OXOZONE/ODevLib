from django.db.models import Q
from django_filters.filters import Filter  # type: ignore

from odevlib.fields.multiple_value_field import MultipleValueField


class MultipleValueFilter(Filter):
    field_class = MultipleValueField

    def __init__(self, *args, field_class, **kwargs):
        kwargs.setdefault('lookup_expr', 'in')
        super().__init__(*args, field_class=field_class, **kwargs)

    def filter(self, qs, value):
        if isinstance(value, str):
            value = value.split(',')
        # if it's not a list then let the parent deal with it
        if self.lookup_expr == 'in' or not isinstance(value, list):
            return super().filter(qs, value)

        # empty list
        if not value:
            return qs
        if self.distinct:
            qs = qs.distinct()

        lookup = '%s__%s' % (self.field_name, self.lookup_expr)
        filters = Q()
        for v in value:
            filters |= Q(**{lookup: v})
        qs = self.get_method(qs)(filters)
        return qs
