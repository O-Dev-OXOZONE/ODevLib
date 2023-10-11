import pytest
from django.contrib.auth.models import AbstractUser, User
from rest_framework.test import APIClient
from odevlib.models.rbac.instance_role_assignment import InstanceRoleAssignment
from odevlib.models.rbac.role import RBACRole
from odevlib.models.rbac.role_assignment import RoleAssignment

from test_app.models import ExampleRBACChild, ExampleRBACParent


@pytest.fixture()
def superuser() -> AbstractUser:
    """
    Create a superuser.
    """
    return User.objects.create_superuser("admin", "admin@example.com", "dummy_password")


@pytest.fixture()
def system_user() -> AbstractUser:
    """
    Create a system user.
    """
    return User.objects.get(username="system")


@pytest.fixture()
def user() -> AbstractUser:
    """
    Create a normal user.
    """
    return User.objects.create_user("user", "user@example.com", "dummy_password")


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture()
def authorized_api_client(api_client: APIClient, user: User) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client


class RBACModelsSetup:
    parent1: ExampleRBACParent
    parent2: ExampleRBACParent
    child1: ExampleRBACChild
    child2: ExampleRBACChild
    child3: ExampleRBACChild
    child4: ExampleRBACChild


@pytest.fixture()
def rbac_models_setup(
    system_user: User,
) -> RBACModelsSetup:
    """
    Create a set of RBAC models for testing.
    """
    setup = RBACModelsSetup()

    setup.parent1 = ExampleRBACParent(test_field="test_field", test_field2="test_field2")
    setup.parent1.save(user=system_user)

    setup.parent2 = ExampleRBACParent(test_field="test_field", test_field2="test_field2")
    setup.parent2.save(user=system_user)

    setup.child1 = ExampleRBACChild(
        parent=setup.parent1,
        test_field3="test_field3",
        test_field4="test_field4",
    )
    setup.child1.save(user=system_user)

    setup.child2 = ExampleRBACChild(
        parent=setup.parent1,
        test_field3="test_field3",
        test_field4="test_field4",
    )
    setup.child2.save(user=system_user)

    setup.child3 = ExampleRBACChild(
        parent=setup.parent2,
        test_field3="test_field3",
        test_field4="test_field4",
    )
    setup.child3.save(user=system_user)

    setup.child4 = ExampleRBACChild(
        parent=setup.parent2,
        test_field3="test_field3",
        test_field4="test_field4",
    )
    setup.child4.save(user=system_user)

    return setup


@pytest.fixture()
def global_role_crud_rbac_setup(
    user: User,
    system_user: User,
) -> None:
    """
    User has global access to all parents.
    """

    role = RBACRole(
        name="test__global_role",
        ui_name="Global role",
        permissions={
            "test_app__examplerbacparent": "crud",
            "test_app__examplerbacchild": "crud",
        },
    )
    role.save(user=system_user)

    assignment = RoleAssignment(
        user=user,
        role=role,
    )
    assignment.save(user=system_user)


@pytest.fixture()
def instance_role_crud_rbac_setup(
    user: User,
    system_user: User,
    rbac_models_setup: RBACModelsSetup,
) -> None:
    """
    User has global access to all parents.
    """

    role = RBACRole(
        name="test__instance_role",
        ui_name="Instance-level role",
        permissions={
            "test_app__examplerbacparent": "crud",
            "test_app__examplerbacchild": "crud",
        },
    )
    role.save(user=system_user)

    assignment = InstanceRoleAssignment(
        user=user,
        role=role,
        model="test_app__examplerbacparent",
        instance_id=rbac_models_setup.parent1.pk,
    )
    assignment.save(user=system_user)
