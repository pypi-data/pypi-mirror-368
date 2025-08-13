from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.generic import View

from django_accounts_api.views.perms import user_has_group_perm, user_has_user_perm

User = get_user_model()

class APIGroupPermissionCreate(View):
    """ Assign a permission to a group
    """

    def post(self, request, group_id, permission_id):
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not user_has_group_perm(request.user, 'change'):
            return HttpResponseForbidden()
        try:
            group = Group.objects.get(
                pk=group_id
            )
        except Group.DoesNotExist:
            return HttpResponseNotFound()
        try:
            permission = Permission.objects.get(
                pk=permission_id
            )
        except Permission.DoesNotExist:
            return HttpResponseNotFound()

        group.permissions.add(permission)
        return HttpResponse(status=201)

class APIUserPermissionCreate(View):
    """ Assign a permission to a user
    """

    def post(self, request, user_id, permission_id):
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not user_has_user_perm(request.user, 'change'):
            return HttpResponseForbidden()
        try:
            user = User.objects.get(
                pk=user_id
            )
        except User.DoesNotExist:
            return HttpResponseNotFound()
        try:
            permission = Permission.objects.get(
                pk=permission_id
            )
        except Permission.DoesNotExist:
            return HttpResponseNotFound()

        user.user_permissions.add(permission)
        return HttpResponse(status=201)
