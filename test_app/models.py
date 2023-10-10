from django.db import models

from odevlib.models.omodel import OModel
from odevlib.models.rbac.mixins import RBACHierarchyModelMixin


class ExampleOModel(OModel):
    """
    Used to test the OModel lifecycle and correctness of created/updated fields logic.

    This model contains a default BigInt primary key.
    """

    test_field = models.TextField()


class ExampleOneToOneOModel(OModel):
    """
    Used to test the OModel lifecycle and correctness of created/updated fields logic.

    This model contains a OneToOneField as primary key.
    """

    sibling = models.OneToOneField(ExampleOModel, on_delete=models.CASCADE, related_name="sibling")
    test_field = models.TextField()


class ExampleRBACParent(OModel):
    test_field = models.TextField()
    test_field2 = models.TextField()


class ExampleRBACChild(RBACHierarchyModelMixin, OModel):
    parent = models.ForeignKey(ExampleRBACParent, on_delete=models.CASCADE, related_name="children")
    test_field3 = models.TextField()
    test_field4 = models.TextField()

    def get_rbac_parent(self) -> ExampleRBACParent | None:
        return self.parent

    @classmethod
    def get_rbac_parent_model(cls: type["ExampleRBACChild"]) -> type[models.Model]:
        return ExampleRBACParent

    @classmethod
    def get_rbac_parent_field_name(cls: type["ExampleRBACChild"]) -> str:
        return "parent"
