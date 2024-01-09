from functools import wraps
from typing import Callable, Any

from django.db import transaction

from odevlib.models.errors import Error


class OAtomic(transaction.Atomic):
    """
    This is a custom Atomic class for odevlib.

    For now, it's not using savepoints and durable mode as it should be used.
    Hope it will be implemented in the future.

    If this class used as context manager, it will start a new transaction or a savepoint.
    If any exception occurred, it will rollback the transaction or to the savepoint.
    In future probably we will check for particular exceptions and rollback only if they occurred.
    """

    def __call__(self, func):
        # Start a new transaction or a savepoint.
        sid = transaction.savepoint(using=self.using)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any | Error:
            result = func(*args, **kwargs)
            if isinstance(result, Error):
                # Rollback the transaction or to the savepoint and return Error instance.
                transaction.savepoint_rollback(sid, using=self.using)
                return result

            # Commit the transaction or release the savepoint and return result.
            transaction.savepoint_commit(sid, using=self.using)
            return result

        return wrapper

    def __enter__(self):
        self.sid = transaction.savepoint(using=self.using)

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(exc_value, Exception):
            # Rollback the transaction or to the savepoint if any exception occurred.
            transaction.savepoint_rollback(self.sid, using=self.using)
        else:
            # Commit the transaction or release the savepoint if no exceptions occurred.
            transaction.savepoint_commit(self.sid, using=self.using)


def odevlib_atomic(using: str | None | Callable = None, savepoint: bool = False, durable: bool = False):
    # Bare decorator: @odevlib_atomic -- although the first argument is called
    # `using`, it's actually the function being decorated.
    if callable(using):
        return OAtomic(using="default", savepoint=savepoint, durable=durable)(using)
    # context manager: with odevlib_atomic(...): ...
    else:
        return OAtomic(using=using, savepoint=savepoint, durable=durable)
