from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.module_loading import import_string


def user_details(user: AbstractUser) -> dict:
    """The details of the user to return on success"""
    extra = {}
    add_extra_path = getattr(settings, "ACCOUNT_API_DETAILS", False)
    if add_extra_path:
        try:
            details_func = import_string(add_extra_path)
            extra = details_func(user)
        except ImportError:
            pass

    return dict(
        id=user.pk,
        name=user.get_full_name(),
        **extra
    )
