import pytest

from odevlib.models.errors import Error
from odevlib.utils.users import get_system_user
from test_app.models import ExampleOModel
from odevlib.decorators.transaction import odevlib_atomic


def function_that_does_some_stuff_and_returns_error(error: bool) -> ExampleOModel | Error:
    first_instanse = ExampleOModel(test_field="Test field 1")
    first_instanse.save(user=get_system_user())
    if error:
        return Error(
            eng_description="Some error eng description",
            ui_description="Some error ui description",
            error_code=1,
        )
    second_instanse = ExampleOModel(test_field="Test field 2")
    second_instanse.save(user=get_system_user())
    return second_instanse


@pytest.mark.django_db
def test_decorator_no_error():
    assert ExampleOModel.objects.count() == 0

    @odevlib_atomic
    def function(error: bool) -> ExampleOModel | Error:
        return function_that_does_some_stuff_and_returns_error(error)

    result = function(error=False)
    assert ExampleOModel.objects.count() == 2
    assert isinstance(result, ExampleOModel)
    assert result.test_field == "Test field 2"


@pytest.mark.django_db
def test_decorator_with_error():
    assert ExampleOModel.objects.count() == 0

    @odevlib_atomic
    def function(error: bool) -> ExampleOModel | Error:
        return function_that_does_some_stuff_and_returns_error(error)

    result = function(error=True)
    assert ExampleOModel.objects.count() == 0
    assert isinstance(result, Error)
    assert result.eng_description == "Some error eng description"
    assert result.ui_description == "Some error ui description"
    assert result.error_code == 1


@pytest.mark.django_db
def test_as_context_manager_no_error():
    assert ExampleOModel.objects.count() == 0

    with odevlib_atomic():
        result = function_that_does_some_stuff_and_returns_error(error=False)

    assert ExampleOModel.objects.count() == 2
    assert isinstance(result, ExampleOModel)
    assert result.test_field == "Test field 2"


@pytest.mark.django_db
def test_as_context_manager_with_error():
    assert ExampleOModel.objects.count() == 0

    try:
        with odevlib_atomic():
            result = function_that_does_some_stuff_and_returns_error(error=True)
            raise Exception("Some exception")
    except Exception:
        print("Ouch! Unexpected exception! Don't worry, all transactions were rolled back!")

    assert ExampleOModel.objects.count() == 0
    assert isinstance(result, Error)
    assert result.eng_description == "Some error eng description"
    assert result.ui_description == "Some error ui description"
    assert result.error_code == 1
