Cookiecutter Template Guide
===========================

Our latest projects are developed using cookiecutter-django template.

It has some imposed structure, and to ease your onboarding toits structure, this document
makes an overview of what's happening.

The project contains several important files and directories:

``.envs`` directory
-------------------

This directory contains the environment variables for each environment. It is
partially ignored by git and only ``local`` environment is commited to the repository.

Upon generation of a project from template, there will also be ``production`` environment,
and the repo creator may use these values to populate CI variables. If repo creator
deletes this folder, maintainers will have to generate values for this environment by hand.


``compose`` directory
---------------------

This directory contains Dockerfiles and everything else needed to build images from these
Dockerfiles. Files are split by environments and services.


``config`` directory
--------------------

This directory contains Django settings, root routers, celery app, WSGI/ASGI settings, etc.

``config/settings/{local.py/production.py/test.py}`` allow to customize settings for
different environments.

``config/settings/base.py`` contains all the settings that are common for all environments.


``docs`` directory
------------------

This directory contains documentation for the project. It is generated using Sphinx.


``{{cookiecutter.project_slug}}`` directory
-------------------------------------------
``project_slug`` is the project name you've chosen while creating the project. All your
subsystems/other source code will usually land here.


``merge_local_dotenvs_in_dotenv.py`` file
-----------------------------------------

This file is used to merge local environment variables from the
``.envs/local/`` directory to ``.env`` file.
It is useful when you want to run the project locally.


``local.yml`` file
------------------

Docker-compose project that you can use to develop locally.


``production.yml`` file
-----------------------

Docker-compose project used when deploying project to production environment.


Other files
-----------

There are also a lot of configs and ignore files, but I'm sure you can figure
this out by yourself.



Single app structure
====================

Your app should generally have the following structure:

.. code-block:: text

    app_name/
        __init__.py
        admin/
            __init__.py
            ...your admin files...
        api/
            __init__.py
            api_router.py (DRF router)
            serializers.py
            views.py
        business_logic/
            __init__.py
            ...your business logic files...
        migrations/
            __init__.py
        models/
            __init__.py
            ...your models...
        tests/
            __init__.py
            api/
                __init__.py
                ...your tests... (Put DRF endpoint tests here)
            business_logic/
                __init__.py
                ...your tests... (Put business logic tests here)
            ...your tests...
        apps.py
        views.py (Django template views)
        urls.py (Django template URLs)


.. admonition:: TODO

    Include ``urls.py`` and ``api_router.py`` examples here.
