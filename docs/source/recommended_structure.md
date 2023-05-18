# Recommended code structure

Generally, we recommend sticking to the functional programming philosophy:
- Use functions instead of classes.
- Use pure functions instead of impure functions whenever possible.
- Use immutable data structures instead of mutable ones.
- NO EXCEPTIONS (there are exceptions to this rule, because we are in Python, though).
- Use type hints everywhere.
- Use `mypy` to ensure type safety.

## What is `mypy`?

Mypy is a static type checker for Python. Currently, it is the most sophisticated type checker, followed by Pyright, then followed by PyCharm's type checker. It's biggest advantage is presence of plugins, which allow type checking for Django. The reason why Django is so hard to type-check can be found [here](why_django_is_hard_to_typecheck).

Mypy is exactly the reason why all code should be type-checked. It helps to isolate the issue to a particular function given the types that the function accepts and returns. All before the code is even executed!

TODO: make my fork of VS Code mypy plugin public and include the link here.

## What the heck are pure functions?

> Pure functions are functions that do not have side effects. They do not modify any global state, they do not modify any mutable arguments, they do not modify any global variables, they do not modify any class variables, they do not modify any class attributes, they do not modify any instance attributes, they do not modify any instance variables, they do not modify any database records, they do not modify any files, they do not modify any network resources, they do not modify any other external resources.
>
> (c) Paragraph courtesy of Copilot.

Generally, the pure function always returns the same result given the same arguments. That implies that it doesn't access files, database, or any other resource not given as argument.

As a consequence, we can unit-test pure functions easily and safely, because we can mock all the arguments. Such function would only change if business logic of a function should change, so, usually, they are left untouched for the lifetime of the project.

Pure functions are always static, not located in any class (they do not have `self` argument).

## How can I handle errors without exceptions?
In Python, the canonical way to handle errors is to raise exceptions. This has its own advantages (exception is an easy way to short-circuit the execution flow), but it also has its own disadvantages (Python does not force function caller to handle the exception with try...except). You can't even know what exceptions can be raised from a function without reading its source code (and all other functions that the given function invokes).

With Django, this becomes a huge pain, because code is so dynamic that we don't know which exceptions can be raised from which functions. So, we have to handle all exceptions in the top-level view, and return 500 error code. This is not good, because we lose the ability to return 400 error code with a meaningful error message, fallback to other handling methods, etc.

Thus, the recommended way is to create functions with the following signature template:

```python
def func(args...) -> Result | Error:
    ...
```
With this approach, we are always forced to handle error in the function caller (remember, we use `mypy`, which forces you to). Yes, this may produce more boilerplate code, but it will be safer and it is less likely you'll need to return to that code in the future.




