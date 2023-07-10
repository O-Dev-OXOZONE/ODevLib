from django.db import models

from odevlib.models.omodel import OModel


class TestOModel(OModel):
    """
    Used to test the OModel lifecycle and correctness of created/updated fields logic.

    This model contains a default BigInt primary key.
    """

    test_field = models.TextField()


class TestOneToOneOModel(OModel):
    """
    Used to test the OModel lifecycle and correctness of created/updated fields logic.

    This model contains a OneToOneField as primary key.
    """

    sibling = models.OneToOneField(TestOModel, on_delete=models.CASCADE, related_name="sibling")
    test_field = models.TextField()
