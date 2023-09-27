import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from odevlib.errors import codes
from odevlib.utils.functional import first
from test_app.models import ExampleOModel


@pytest.fixture()
@pytest.mark.django_db()
def populated_example_omodel(superuser: User) -> list[ExampleOModel]:
    return ExampleOModel.objects.bulk_create(
        ExampleOModel(
            id=i + 1,
            test_field=f"test {i + 1}",
            created_by=superuser,
            updated_by=superuser,
        )
        for i in range(100)
    )


@pytest.mark.django_db()
def test_example_omodel_list(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/example_omodel/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 100


@pytest.mark.django_db()
def test_example_omodel_retrieve(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],
    superuser: User,
) -> None:
    response = authorized_api_client.get("/test_app/example_omodel/1/")
    instance: ExampleOModel | None = first(filter(lambda x: x.id == 1, populated_example_omodel))
    assert instance is not None

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "test_field": "test 1",
        "created_by": superuser.id,
        "updated_by": superuser.id,
        "created_at": instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_at": instance.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }


@pytest.mark.django_db()
def test_example_omodel_create(authorized_api_client: APIClient, user: User) -> None:
    response = authorized_api_client.post(
        "/test_app/example_omodel/",
        {
            "test_field": "test",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
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


@pytest.mark.django_db()
def test_example_omodel_update(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],
    user: User,
) -> None:
    response = authorized_api_client.patch(
        "/test_app/example_omodel/1/",
        {
            "test_field": "test",
        },
    )
    instance: ExampleOModel | None = first(filter(lambda x: x.id == 1, populated_example_omodel))
    updated_instance = ExampleOModel.objects.get(id=1)
    assert instance is not None

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "test_field": "test",
        "created_by": instance.created_by.id,
        "updated_by": user.id,
        "created_at": instance.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_at": updated_instance.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }


@pytest.mark.django_db()
def test_example_omodel_delete(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.delete("/test_app/example_omodel/1/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    assert ExampleOModel.objects.filter(id=1).count() == 0


@pytest.mark.django_db()
def test_example_omodel_list_paginated(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=10")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 10
    assert "x-odevlib-has-more" in response.headers
    assert response.headers["x-odevlib-has-more"] == "true"


@pytest.mark.django_db()
def test_example_omodel_list_paginated_with_last_id(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=10&last_id=10")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 10
    assert "x-odevlib-has-more" in response.headers
    assert response.headers["x-odevlib-has-more"] == "true"


@pytest.mark.django_db()
def test_example_omodel_list_paginated_with_last_id_end_of_list(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=10&last_id=90")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 10
    assert "x-odevlib-has-more" in response.headers
    assert response.headers["x-odevlib-has-more"] == "false"


@pytest.mark.django_db()
def test_example_omodel_list_paginated_with_last_id_end_of_list_less_than_count(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=10&last_id=91")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 9
    assert "x-odevlib-has-more" in response.headers
    assert response.headers["x-odevlib-has-more"] == "false"


@pytest.mark.django_db()
def test_example_omodel_list_paginated_with_first_id(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=10&first_id=10")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 9
    assert "x-odevlib-has-more" in response.headers
    assert response.headers["x-odevlib-has-more"] == "false"


@pytest.mark.django_db()
def test_example_omodel_list_paginated_with_first_id_start_of_list(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=10&first_id=100")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 10
    assert "x-odevlib-has-more" in response.headers
    assert response.headers["x-odevlib-has-more"] == "true"


@pytest.mark.django_db()
def test_example_omodel_list_paginated_with_invalid_first_id(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=10&first_id=not_a_number")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "error_code": codes.invalid_request_data,
        "eng_description": "first_id must be int",
        "ui_description": "first_id must be int",
    }


@pytest.mark.django_db()
def test_example_omodel_list_paginated_with_invalid_count(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=not_a_number")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "error_code": codes.invalid_request_data,
        "eng_description": "count must be int",
        "ui_description": "count must be int",
    }


@pytest.mark.django_db()
def test_example_omodel_list_paginated_with_invalid_last_id(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=10&last_id=not_a_number")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "error_code": codes.invalid_request_data,
        "eng_description": "last_id must be int",
        "ui_description": "last_id must be int",
    }


@pytest.mark.django_db()
def test_example_omodel_list_paginated_with_both_first_id_and_last_id(
    authorized_api_client: APIClient,
    populated_example_omodel: list[ExampleOModel],  # noqa: ARG001
) -> None:
    response = authorized_api_client.get("/test_app/paginated_example_omodel/?count=10&first_id=10&last_id=10")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "error_code": codes.invalid_request_data,
        "eng_description": "Can't use both first_id and last_id. Please specify only one argument.",
        "ui_description": "Can't use both first_id and last_id. Please specify only one argument.",
    }
