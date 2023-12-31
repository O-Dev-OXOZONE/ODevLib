from . import exceptions as exceptions
from .manager import HistoryDescriptor as HistoryDescriptor, SIMPLE_HISTORY_REVERSE_ATTR_NAME as SIMPLE_HISTORY_REVERSE_ATTR_NAME
from .signals import post_create_historical_record as post_create_historical_record, pre_create_historical_record as pre_create_historical_record
from .utils import get_change_reason_from_object as get_change_reason_from_object
from _typeshed import Incomplete
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor, ReverseManyToOneDescriptor
from django.db.models.query import QuerySet as QuerySet
from simple_history import utils as utils

registered_models: Incomplete

class HistoricalRecords:
    thread: Incomplete
    context: Incomplete
    m2m_models: Incomplete
    user_set_verbose_name: Incomplete
    user_set_verbose_name_plural: Incomplete
    user_related_name: Incomplete
    user_db_constraint: Incomplete
    table_name: Incomplete
    inherit: Incomplete
    history_id_field: Incomplete
    history_change_reason_field: Incomplete
    user_model: Incomplete
    get_user: Incomplete
    cascade_delete_history: Incomplete
    custom_model_name: Incomplete
    app: Incomplete
    user_id_field: Incomplete
    user_getter: Incomplete
    user_setter: Incomplete
    related_name: Incomplete
    use_base_model_db: Incomplete
    m2m_fields: Incomplete
    no_db_index: Incomplete
    excluded_fields: Incomplete
    excluded_field_kwargs: Incomplete
    bases: Incomplete
    def __init__(self, verbose_name: Incomplete | None = ..., verbose_name_plural: Incomplete | None = ..., bases=..., user_related_name: str = ..., table_name: Incomplete | None = ..., inherit: bool = ..., excluded_fields: Incomplete | None = ..., history_id_field: Incomplete | None = ..., history_change_reason_field: Incomplete | None = ..., user_model: Incomplete | None = ..., get_user=..., cascade_delete_history: bool = ..., custom_model_name: Incomplete | None = ..., app: Incomplete | None = ..., history_user_id_field: Incomplete | None = ..., history_user_getter=..., history_user_setter=..., related_name: Incomplete | None = ..., use_base_model_db: bool = ..., user_db_constraint: bool = ..., no_db_index=..., excluded_field_kwargs: Incomplete | None = ..., m2m_fields=...) -> None: ...
    manager_name: Incomplete
    module: Incomplete
    cls: Incomplete
    def contribute_to_class(self, cls, name) -> None: ...
    skip_history_when_saving: bool
    def add_extra_methods(self, cls): ...
    def finalize(self, sender, **kwargs) -> None: ...
    def get_history_model_name(self, model): ...
    def create_history_m2m_model(self, model, through_model): ...
    def create_history_model(self, model, inherited): ...
    def fields_included(self, model): ...
    def field_excluded_kwargs(self, field): ...
    def copy_fields(self, model): ...
    def get_extra_fields(self, model, fields): ...
    def get_meta_options(self, model): ...
    def post_save(self, instance, created, using: Incomplete | None = ..., **kwargs) -> None: ...
    def post_delete(self, instance, using: Incomplete | None = ..., **kwargs) -> None: ...
    def get_change_reason_for_object(self, instance, history_type, using): ...
    def m2m_changed(self, instance, action, attr, pk_set, reverse, **_) -> None: ...
    def create_historical_record_m2ms(self, history_instance, instance) -> None: ...
    def create_historical_record(self, instance, history_type, using: Incomplete | None = ...) -> None: ...
    def get_history_user(self, instance): ...

def transform_field(field) -> None: ...

class HistoricForwardManyToOneDescriptor(ForwardManyToOneDescriptor):
    def get_queryset(self, **hints) -> QuerySet: ...

class HistoricReverseManyToOneDescriptor(ReverseManyToOneDescriptor):
    def related_manager_cls(self): ...

class HistoricForeignKey(ForeignKey):
    forward_related_accessor_class: Incomplete
    related_accessor_class: Incomplete

def is_historic(instance): ...
def to_historic(instance): ...

class HistoricalObjectDescriptor:
    model: Incomplete
    fields_included: Incomplete
    def __init__(self, model, fields_included) -> None: ...
    def __get__(self, instance, owner): ...

class HistoricalChanges:
    def diff_against(self, old_history, excluded_fields: Incomplete | None = ..., included_fields: Incomplete | None = ...): ...

class ModelChange:
    field: Incomplete
    old: Incomplete
    new: Incomplete
    def __init__(self, field_name, old_value, new_value) -> None: ...

class ModelDelta:
    changes: Incomplete
    changed_fields: Incomplete
    old_record: Incomplete
    new_record: Incomplete
    def __init__(self, changes, changed_fields, old_record, new_record) -> None: ...
