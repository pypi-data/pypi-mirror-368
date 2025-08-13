from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from django_accounts_api.views.json_list_view import JsonListView
from django_accounts_api.views.perms import user_has_any_group_perm


@method_decorator(never_cache, name='dispatch')
class APIGroupsView(JsonListView):
    ''' Returns a json serialized list of user groups


    '''
    model = Group

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not user_has_any_group_perm(request.user):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


    def get_fields(self):
        return ['name']
