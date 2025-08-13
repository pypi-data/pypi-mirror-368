import re
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group

User = get_user_model()

def is_user_perm(perm_codename: str):
    ''' returns true if the permission codename relates to the configured user model'''
    match =  re.match(
        f'^{User._meta.app_label}\.[\w]+_{User._meta.model_name}',
        perm_codename
    )
    return match

def is_group_perm(perm_codename: str):
    ''' returns true if the permission codename relates to the Group model'''
    match =  re.match(
        f'^{Group._meta.app_label}\.[\w]+_{Group._meta.model_name}',
        perm_codename
    )
    return match

def user_has_any_user_perm(user: AbstractUser):
    ''' returns true if the user has any permission related to the configured user model'''
    perms = user.get_all_permissions()
    return any(
        filter(
            lambda perm: is_user_perm(perm),
            perms
        )
    )

def user_has_any_group_perm(user: AbstractUser):
    ''' returns true if the user has any permission related to the configured user model'''
    perms = user.get_all_permissions()
    return any(
        filter(
            lambda perm: is_group_perm(perm),
            perms
        )
    )

def user_has_user_perm(user: AbstractUser, perm: str):
    ''' returns true if the user has the specified permission on the configured user model'''
    return user.has_perm(f'{User._meta.app_label}.{perm}_{User._meta.model_name}')

def user_has_group_perm(user: AbstractUser, perm: str):
    ''' returns true if the user has the specified permission on the group model'''
    return user.has_perm(f'{Group._meta.app_label}.{perm}_{Group._meta.model_name}')
