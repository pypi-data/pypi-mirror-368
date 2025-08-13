from django.contrib.auth.models import AbstractBaseUser, Group, Permission
from django.contrib.contenttypes.models import ContentType


def add_group_permission(user: AbstractBaseUser, permission: str):
    user.user_permissions.add(
        Permission.objects.get(
            content_type=ContentType.objects.get_for_model(Group),
            codename=f"{permission}_{Group._meta.model_name}"
        )
    )
