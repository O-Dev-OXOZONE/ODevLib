Recommended code structure
==========================

Generally, we recommend sticking to the functional programming philosophy:
  - Use functions instead of classes.
  - Use pure functions instead of impure functions whenever possible.
  - Use immutable data structures instead of mutable ones.
  - NO EXCEPTIONS (there are exceptions to this rule, because we are in Python, though).
  - Use type hints everywhere.
  - Use ``mypy`` to ensure type safety.

What is ``mypy``?
---------------

Mypy is a static type checker for Python. Currently, it is the most sophisticated type checker, followed by Pyright, then followed by PyCharm's type checker. It's biggest advantage is presence of plugins, which allow type checking for Django. The reason why Django is so hard to type-check can be found `here <why_django_is_hard_to_typecheck>`_.

Mypy is exactly the reason why all code should be type-hinted. It helps to isolate the issue to a particular function, given the types that the function accepts and returns. All done before the code is even executed!

TODO: make my fork of VS Code mypy plugin public and include the link here.

What the heck are pure functions?
---------------------------------

.. admonition:: AI thoughts

    Pure functions are functions that do not have side effects. They do not modify any global state, they do not modify any mutable arguments, they do not modify any global variables, they do not modify any class variables,   they do not modify any class attributes, they do not modify any instance attributes, they do not modify any instance variables, they do not modify any database records, they do not modify any files, they do not modify any network resources, they do not modify any other external resources.

    © Paragraph courtesy of Copilot.

Ignoring errors is out of question in this discussion, because it will inevitably lead to software bugs and flaws.

Most straightforward description is: a pure function always returns the same result given the same arguments. That implies that it doesn't access files, database, or any other resource not given as argument.

As a consequence, we can unit-test pure functions easily and safely, because we can mock all the arguments. Code of such function would only change if business logic of a function should change, so, usually, they are left untouched for the lifetime of the project.

Pure functions are always global/static, not located in any class (they do not have ``self`` argument).

What are immutable data structures and why should I care?
---------------------------------------------------------

Immutable data structures are ones that can't be modified after they are created. Remember the pure functions? Pure functions are only possible with immutable data structures. If you pass a mutable data structure to a pure function, it can modify the data passed from outside, and thus it will not be pure anymore.

Immutable data structures are slower than mutable ones, but they are much safer. They are also easier to reason about, because you can be sure that the data you passed to a function will not be modified by that function.

Some built-in immutable data structures include ``tuple``, ``frozenset``, ``str``, ``bytes``, ``int``, ``float``, ``bool``, ``None``. Some built-in mutable data structures include ``list``, ``set``, ``dict``.

The easiest way to create own immutable structure in Python is to use dataclasses with ``frozen=True``. This overrides ``__setattr__`` and ``__delattr__`` methods to raise an exception if you try to modify any attribute of the dataclass:

.. code-block:: python

    @dataclass(frozen=True)
    class Foo:
        bar: int

    foo = Foo(1)
    foo.bar = 2  # raises an exception

It does not make the dataclass deeply immutable (i.e. if you create immutable dataclass with list, the list still can be modified):

.. code-block:: python

    @dataclass(frozen=True)
    class Foo:
        bar: list

    foo = Foo([1, 2, 3])
    foo.bar.append(4)  # no exception raised

Even if you are lazy or immutable data structures are not suitable for your use case, you should still use ``dataclass`` (without ``frozen=True``) to define your data structures. They are much easier to reason about than ``dict`` or ``tuple``, and provide static type checking.

How can I handle errors without exceptions?
-------------------------------------------

In Python, the canonical way to handle errors is to **raise exceptions**. This has its own advantages (exception is an easy way to short-circuit the execution flow), but it also has its own disadvantages (Python does not force function caller to handle the exception with try...except). You can't even know what exceptions can be raised from a function without reading its source code (and all other functions that the given function invokes).

With Django, this becomes a huge pain, because code is so dynamic that we don't know which exceptions can be raised from which functions. So, we have to handle all exceptions in the top-level function of a view, and return 500 error code if some exception was not handled. This is not good, because we lose the ability to return 400 error code with a meaningful error message, fallback to other handling methods, etc. API endpoint caller can only see that *some* error happened, but can't know what exactly happened.

Thus, the recommended way is to create functions with the following structure:

.. code-block:: python

    def func(args...) -> Result | Error:
        ...

        # In case error occurred
        return Error(
            error_code=codes.invalid_request_data,
            eng_description="Technical description",
            ui_description="User-friendly description which is shown to the user",
        )

        ...

        # In case everything is OK
        return result


.. Warning::
  
  Keep in mind that all of these three fields are returned to the frontend, so don't put sensitive data into ``eng_description``.

To handle the error, you can use the following structure (but it is not mandatory):

.. code-block:: python

    result = func(args...)
    if isinstance(result, Error):
        # In case the error should be propagated to the caller,
        # you can simply return the error.
        return result

        # In case the error should be handled here, your custom
        # logic should be placed instead.

    # continue with the happy path

With this approach, we are always forced to handle error in the function caller (remember, we use ``mypy``, which forces you to). Yes, this may produce more boilerplate code, but it will be safer and it is less likely you'll need to return to that code in the future.

The exception I mentioned earlier is ``__init__`` method. It does not return anything by design, so unfortunately there is no way to report error from ``__init__`` other than throwing an exception.

Conclusion
++++++++++

Sticking with returning errors instead of throwing them allows to minimize developer time spent on code reading, because all information is presented at a glance in the function signature.

