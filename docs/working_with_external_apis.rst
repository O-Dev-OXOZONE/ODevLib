Working with external APIs
==========================

Sometimes, external APIs have an associated Python library.
In this case, we recommend using a library, since libraries usually
include types (classes for each API entity, etc.).

But what should you do when there's no library? 99% of the time, you have JSON REST API.
Since we recommend to maximize amount of typed code, the way to go is to implement
Pydantic models for each entity of the API, and convert HTTP responses to these models
as soon as possible.

The earlier you convert JSON to a validated Pydantic model, the earlier you will catch
a potential error. Plus, you minimize the scope that such error may affect.

So, let's imagine you have a API wrapper for service Foo. Instead of doing this:

.. code-block:: python

    class FooAPI:
        """
        Class that actually does the HTTP requests to the external service
        """

        def get_users() -> list[dict] | Error:
            ...


    class User(BaseModel):
        """
        Pydantic model for the user.
        """

        id: int
        name: str
        email: str


    class FooBusinessLogic:
        def get_users(response: list[dict]) -> list[User] | Error:
            # parse list of dicts to pydanitc model User, catching the errors
            try:
                users = [User(**user) for user in response]
            except ValidationError as e:
                return Error(
                    error_code=codes.internal_server_error,
                    eng_description=str(e),
                    ui_description="Failed to parse response from Foo API",
                )


You can do:

.. code-block:: python

    class User(BaseModel):
        """
        Pydantic model for the user.
        """

        id: int
        name: str
        email: str


    class FooAPI:
        ...

        def get_users() -> list[User] | Error:
            # do request
            response = requests.get(...)

            # parse list of dicts to pydanitc model User, catching the errors
            try:
                return [User(**user) for user in response.json()]
            except ValidationError as e:
                return Error(
                    error_code=codes.internal_server_error,
                    eng_description=str(e),
                    ui_description="Failed to parse response from Foo API",
                )

Now, the scope for possible model/data inconsistency is minimized from 2 functions to 1 function.
