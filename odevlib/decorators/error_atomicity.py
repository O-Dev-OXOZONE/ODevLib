from typing import Callable, Any
from django.db import transaction

from odevlib.exceptions.integrity import OdevlibIntegrityError
from odevlib.models.errors import Error


def check_error(func) -> Callable:
    """
    This decorator should check if decorated function returns instance of Error
    if it does, then it should raise OdevlibIntegrityError
    This is going to rollback transaction
    """
    def wrapper(*args, **kwargs) -> Any | Error:
        result = func(*args, **kwargs)
        if isinstance(result, Error):
            raise OdevlibIntegrityError(
                eng_description=result.eng_description,
                ui_description=result.ui_description,
                error_code=result.error_code,
            )
        return result

    return wrapper


def odevlib_transaction_atomic(func) -> Callable:
    """
    This decorator takes function and wraps it in check_error decorator
    Then it tries to execute wrapped function in transaction.atomic()
    If OdevlibIntegrityError is raised, it returns Error instance
    """
    def wrapper(*args, **kwargs) -> Any | Error:
        try:
            with transaction.atomic():
                decorated_func = check_error(func)
                return decorated_func(*args, **kwargs)
        except OdevlibIntegrityError as e:
            return Error(
                eng_description=e.eng_description,
                ui_description=e.ui_description,
                error_code=e.error_code,
            )

    return wrapper
