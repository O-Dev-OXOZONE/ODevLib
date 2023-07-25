import pytest
from django.contrib.auth import get_user_model
from test_app.models import TestOneToOneOModel

from test_app.models import TestOModel
from django.contrib.auth.models import User


@pytest.fixture
def test_omodel(user: User) -> TestOModel:
    model = TestOModel(test_field="Test value")
    model.save(user=user)
    return model


@pytest.mark.django_db
def test_omodel_lifecycle(user: User):
    instance = TestOModel(test_field="Test value")
    instance.save(user=user)

    created_at = instance.created_at
    updated_at = instance.updated_at

    instance.test_field = "Test value 2"
    instance.save(user=user)

    assert instance.created_at == created_at
    assert instance.updated_at > updated_at


@pytest.mark.django_db
def test_omodel_lifecycle_with_one_to_one(user: User, test_omodel: TestOModel):
    instance = TestOneToOneOModel(sibling=test_omodel, test_field="Test value")
    instance.save(user=user)

    created_at = instance.created_at
    updated_at = instance.updated_at

    instance.test_field = "Test value 2"
    instance.save(user=user)

    assert instance.created_at == created_at
    assert instance.updated_at > updated_at
