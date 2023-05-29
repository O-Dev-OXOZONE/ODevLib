Managing environment variables
==============================

The way that developers handle environment variables is a bit of a mess.
There are so many ways that it comes down to the code style preferences.

In O.dev, we stick to
`django-cookiecutter <https://github.com/cookiecutter/cookiecutter-django>`_
template lately. So, variables are stored in the ``.envs`` directory in the
root of a project:

.. code-block::

    .
    ├── .envs               (dir)
    │   ├── .local          (dir)
    │   │   ├── .django     (file)
    │   │   ├── .postgres   (file)
    │   │   └── .external   (file)
    │   ├── .production     (dir)
    │   │   ├── .django     (file)
    │   │   ├── .postgres   (file)
    │   │   └── .external   (file)
    ...

Every file contains environment variables for a specific environment and 
specific scope.

In the code, we load all variables in the Django settings module:

.. code-block:: python

    # This snippet is already included in the settings file.
    # You don't need to paste it.
    import environ
    env = environ.Env()
    READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
    if READ_DOT_ENV_FILE:
        env.read_env(str(BASE_DIR / ".env"))
    # Snippet end

    # ... some more settings ...

    # In the end of the file, add your env variables like this:
    INFURA_KEY = env("INFURA_KEY")

    # Or, you can import specific types, and even add defaults
    DEBUG = env.bool("DJANGO_DEBUG", False)

In the places where you need a variable value, you can import it from the settings:

.. code-block:: python

    from django.conf import settings

    infura_key = settings.INFURA_KEY

When running locally (even without Docker), you will need to merge all env files
for a particular environment into one file. You can do it with the following
script, included in the repo:

.. code-block:: bash

    python merge_local_dotenvs_in_dotenv.py

This script will produce a ``.env`` file in the root of the project.
You can/should tune the collected variables for your needs (i.e. by default,
``POSTGRES_DB`` will be set to ``postgres``, which is only valid in Docker,
as Docker's DNS server maps this to the correct container). When running locally,
you should change this to ``localhost`` (don't forget to expose the database port
in the docker compose config).

That should be it.
