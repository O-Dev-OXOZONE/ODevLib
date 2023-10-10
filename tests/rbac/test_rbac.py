import pytest
from rest_framework import status
from rest_framework.test import APIClient

from tests.conftest import RBACModelsSetup


@pytest.mark.django_db()
def test_global_role_crud_list_parents(
    authorized_api_client: APIClient,
    rbac_models_setup: RBACModelsSetup,
    global_role_crud_rbac_setup: None,
) -> None:
    response = authorized_api_client.get("/test_app/example_rbac_parent/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    body = response.json()
    assert body == [
        {
            "id": rbac_models_setup.parent1.pk,
            "test_field": rbac_models_setup.parent1.test_field,
            "test_field2": rbac_models_setup.parent1.test_field2,
        },
        {
            "id": rbac_models_setup.parent2.pk,
            "test_field": rbac_models_setup.parent2.test_field,
            "test_field2": rbac_models_setup.parent2.test_field2,
        },
    ]


@pytest.mark.django_db()
def test_global_role_crud_list_children(
    authorized_api_client: APIClient,
    rbac_models_setup: RBACModelsSetup,
    global_role_crud_rbac_setup: None,
) -> None:
    response = authorized_api_client.get("/test_app/example_rbac_child/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 4
    body = response.json()
    assert body == [
        {
            "id": rbac_models_setup.child1.pk,
            "parent": rbac_models_setup.child1.parent.pk,
            "test_field3": rbac_models_setup.child1.test_field3,
            "test_field4": rbac_models_setup.child1.test_field4,
        },
        {
            "id": rbac_models_setup.child2.pk,
            "parent": rbac_models_setup.child2.parent.pk,
            "test_field3": rbac_models_setup.child2.test_field3,
            "test_field4": rbac_models_setup.child2.test_field4,
        },
        {
            "id": rbac_models_setup.child3.pk,
            "parent": rbac_models_setup.child3.parent.pk,
            "test_field3": rbac_models_setup.child3.test_field3,
            "test_field4": rbac_models_setup.child3.test_field4,
        },
        {
            "id": rbac_models_setup.child4.pk,
            "parent": rbac_models_setup.child4.parent.pk,
            "test_field3": rbac_models_setup.child4.test_field3,
            "test_field4": rbac_models_setup.child4.test_field4,
        },
    ]
