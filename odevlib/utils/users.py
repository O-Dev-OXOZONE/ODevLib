from django.contrib.auth import get_user_model


def get_system_user():
    """Returns the ODevLib system user."""
    return get_user_model().objects.get(username="system")
