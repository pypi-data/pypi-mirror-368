from functools import reduce
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import View
from django_accounts_api.views.permissions.permissions_filter import PermissionFilter, combine_filters

from django_accounts_api.views.perms import user_has_any_group_perm, user_has_any_user_perm

User = get_user_model()

def relevant_permission_model_code_filters():
    return [
        PermissionFilter(User),
        PermissionFilter(Group),
    ]

@method_decorator(never_cache, name='dispatch')
class APIPermissionsView(View):
    ''' Returns a json serialized list of assigned permissions
    Filtered by setting.ACCOUNTS_API_RELEVANT_PERMISSIONS
    Separated into group and user sections
    '''

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        has_user_perm = user_has_any_user_perm(request.user)
        has_group_perm = user_has_any_group_perm(request.user)
        if not has_user_perm and not has_group_perm:
            return HttpResponseForbidden()

        ps = Permission.objects.filter(
            combine_filters(relevant_permission_model_code_filters())
        ).prefetch_related('group_set', 'user_set')

        body = reduce(
            get_perms_body_reducer(has_user_perm, has_group_perm),
            ps,
            {}
        )
        return JsonResponse(body)

def get_perms_body_reducer(user_perms, group_perms):

    def perms_body_reduce(result: dict, perm: Permission):
        nonlocal user_perms, group_perms
        perms = result.setdefault('permissions', {})
        perms[perm.pk] = perm.name
        if user_perms:
            all_user_perms = result.setdefault('user_perms', {})
            for user in perm.user_set.all():
                user_user_perms: list[int] = all_user_perms.setdefault(user.pk, [])
                user_user_perms.append(perm.pk)
        if group_perms:
            all_group_perms = result.setdefault('group_perms', {})
            for group in perm.group_set.all():
                group_group_perms: list[int] = all_group_perms.setdefault(group.pk, [])
                group_group_perms.append(perm.pk)
        return result

    return perms_body_reduce
