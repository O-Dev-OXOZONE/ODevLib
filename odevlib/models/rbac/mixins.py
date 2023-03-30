import abc
from typing import Optional, Type

from django.db import models


class RBACHierarchyModelMixin:
    """
    This mixin can be used to mark model as participating in the RBAC hierarchy.

    It forces to define `get_rbac_parent` method, which returns a parent model instance for a 
    particular child instance.
    """

    @abc.abstractmethod
    def get_rbac_parent(self) -> Optional[models.Model]:
        """
        Returns instance of the parent model. RBAC tries to check not only the roles of the model
        itself, but also its parents.

        Example: if order model has get_rbac_parent() which returns user model of the customer who
        made the order, having access to that user will also give access to all their orders.
        """

    @classmethod
    @abc.abstractmethod
    def get_rbac_parent_model(cls) -> Type[models.Model]:
        """
        Returns parent model class. Parent model class is used to check RBAC permissions when
        creating a new instance of this model.
        """

    @classmethod
    @abc.abstractmethod
    def get_rbac_parent_field_name(cls) -> str:
        """
        Returns name of the field in the serializer that specifies ID of the parent instance.
        """
