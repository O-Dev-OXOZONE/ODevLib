from .. import compat as compat
from .filters import BooleanFilter as BooleanFilter, IsoDateTimeFilter as IsoDateTimeFilter
from _typeshed import Incomplete
from .. import filterset as filterset

FILTER_FOR_DBFIELD_DEFAULTS: Incomplete

class FilterSet(filterset.FilterSet):
    FILTER_DEFAULTS: Incomplete
    @property
    def form(self): ...
