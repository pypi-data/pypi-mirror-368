from functools import reduce
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import View

from django_accounts_api.views.perms import user_has_user_perm

User = get_user_model()


@method_decorator(never_cache, name='dispatch')
class APIMembershipUserView(View):
    ''' Returns a json serialized list of groups a user is a member of
    '''

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.user_id = kwargs.get('user_id', None)
        self.group_id = kwargs.get('group_id', None)
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not user_has_user_perm(request.user, 'view'):
            return HttpResponseForbidden()

        users = User.objects.prefetch_related('groups')
        if self.user_id:
            users = users.filter(pk=self.user_id)

        body = reduce(
            membership_body_reduce,
            users,
            {}
        )
        return JsonResponse(body)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not user_has_user_perm(request.user, 'change'):
            return HttpResponseForbidden()
        if not self.user_id or not self.group_id:
            return HttpResponseBadRequest(
                "You must provide both user and group ids to add membership"
            )
        try:
            user = User.objects.get(pk=self.user_id)
        except User.DoesNotExist:
            return HttpResponseNotFound()
        try:
            group = Group.objects.get(pk=self.group_id)
        except Group.DoesNotExist:
            return HttpResponseNotFound()

        user.groups.add(group)
        return HttpResponse(status=201)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not user_has_user_perm(request.user, 'change'):
            return HttpResponseForbidden()
        if not self.user_id or not self.group_id:
            return HttpResponseBadRequest(
                "You must provide both user and group ids to add membership"
            )
        try:
            user = User.objects.get(pk=self.user_id)
        except User.DoesNotExist:
            return HttpResponseNotFound()
        try:
            group = Group.objects.get(pk=self.group_id)
        except Group.DoesNotExist:
            return HttpResponseNotFound()

        user.groups.remove(group)
        return HttpResponse(status=200)


def membership_body_reduce(result: dict, user: User):
    groups: list = result.setdefault(user.pk, [])
    for group in user.groups.all():
        groups.append(group.pk)
    return result
