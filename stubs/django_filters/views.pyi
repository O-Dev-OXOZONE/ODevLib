from .constants import ALL_FIELDS as ALL_FIELDS
from .filterset import filterset_factory as filterset_factory
from .utils import MigrationNotice as MigrationNotice, RenameAttributesBase as RenameAttributesBase
from _typeshed import Incomplete
from django.views.generic import View
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin

class FilterMixinRenames(RenameAttributesBase):
    renamed_attributes: Incomplete

class FilterMixin(metaclass=FilterMixinRenames):
    filterset_class: Incomplete
    filterset_fields: Incomplete
    strict: bool
    def get_filterset_class(self): ...
    def get_filterset(self, filterset_class): ...
    def get_filterset_kwargs(self, filterset_class): ...
    def get_strict(self): ...

class BaseFilterView(FilterMixin, MultipleObjectMixin, View):
    filterset: Incomplete
    object_list: Incomplete
    def get(self, request, *args, **kwargs): ...

class FilterView(MultipleObjectTemplateResponseMixin, BaseFilterView):
    template_name_suffix: str

def object_filter(request, model: Incomplete | None = ..., queryset: Incomplete | None = ..., template_name: Incomplete | None = ..., extra_context: Incomplete | None = ..., context_processors: Incomplete | None = ..., filter_class: Incomplete | None = ...): ...
