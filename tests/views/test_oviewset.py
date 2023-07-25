from datetime import UTC
from django.contrib.auth.models import User
import pytest
from rest_framework.test import APIClient
from odevlib.utils.functional import first

from test_app.models import ExampleOModel


@pytest.fixture
@pytest.mark.django_db
def populated_example_omodel(superuser: User) -> None:
    return ExampleOModel.objects.bulk_create(
        ExampleOModel(
            id=i,
            test_field=f"test {i}",
            created_by=superuser,
            updated_by=superuser,
        )
        for i in range(100)
    )


@pytest.mark.django_db
def test_example_omodel_list(
    authorized_api_client: APIClient, populated_example_omodel
) -> None:
    response = authorized_api_client.get("/test_app/example_omodel/")
    assert response.status_code == 200
    assert len(response.json()) == 100


@pytest.mark.django_db
def test_example_omodel_retrieve(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],
    superuser: User,
) -> None:
    response = authorized_api_client.get("/test_app/example_omodel/1/")
    instance: ExampleOModel | None = first(
        filter(lambda x: x.id == 1, populated_example_omodel)
    )
    assert instance is not None

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "test_field": "test 1",
        "created_by": superuser.id,
        "updated_by": superuser.id,
        "created_at": instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_at": instance.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }


@pytest.mark.django_db
def test_example_omodel_create(authorized_api_client: APIClient, user: User) -> None:
    response = authorized_api_client.post(
        "/test_app/example_omodel/",
        {
            "test_field": "test",
        },
    )
    assert response.status_code == 201
    json = response.json()
    # id has a random auto-incremented value, it makes no sense to test for it
    json.pop("id")
    assert response.json() == {
        "test_field": "test",
        "created_by": user.id,
        "updated_by": user.id,
        "created_at": response.json()["created_at"],
        "updated_at": response.json()["updated_at"],
    }


@pytest.mark.django_db
def test_example_omodel_update(
    authorized_api_client: APIClient, populated_example_omodel: list[ExampleOModel], user: User
) -> None:
    response = authorized_api_client.patch(
        "/test_app/example_omodel/1/",
        {
            "test_field": "test",
        },
    )
    instance: ExampleOModel | None = first(
        filter(lambda x: x.id == 1, populated_example_omodel)
    )
    updated_instance = ExampleOModel.objects.get(id=1)
    assert instance is not None

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "test_field": "test",
        "created_by": instance.created_by.id,
        "updated_by": user.id,
        "created_at": instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_at": updated_instance.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }


@pytest.mark.django_db
def test_example_omodel_delete(
    authorized_api_client: APIClient, populated_example_omodel: list[ExampleOModel]
) -> None:
    response = authorized_api_client.delete("/test_app/example_omodel/1/")
    assert response.status_code == 204
    assert response.content == b''
    assert ExampleOModel.objects.filter(id=1).count() == 0