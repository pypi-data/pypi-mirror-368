from functools import reduce
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import View

from django_accounts_api.views.perms import user_has_group_perm

User = get_user_model()


@method_decorator(never_cache, name='dispatch')
class APIMembershipGroupView(View):
    ''' Returns a json serialized list of members of a group
    '''

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not user_has_group_perm(request.user, 'view'):
            return HttpResponseForbidden()

        groups = Group.objects.prefetch_related('user_set')
        group_id = kwargs.get('group_id', None)
        if group_id:
            groups = groups.filter(pk=group_id)

        body = reduce(
            membership_body_reduce,
            groups,
            {}
        )
        return JsonResponse(body)


def membership_body_reduce(result: dict, group: Group):
    users: list = result.setdefault(group.pk, [])
    for user in group.user_set.all():
        users.append(user.pk)
    return result
