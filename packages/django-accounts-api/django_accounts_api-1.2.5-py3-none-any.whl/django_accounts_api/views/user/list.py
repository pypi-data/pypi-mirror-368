from typing import Any
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from django_accounts_api.views.json_list_view import JsonListView
from django_accounts_api.views.perms import user_has_any_user_perm

User = get_user_model()

# Setting to control the fields returned by the user api
USER_FIELD_SETTTING = 'ACCOUNTS_API_USER_FIELDS'
# Default fields returned byt he user aPI if no setting provided
DEFAULT_USER_FIELDS = [
    'username',
    'first_name',
    'last_name',
    'email',
    'last_login',
    'is_active',
]


@method_decorator(never_cache, name='dispatch')
class APIUsersView(JsonListView):
    ''' Returns a json serialized list of user models


    '''
    model = User
    fields_setting_name = None

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not user_has_any_user_perm(request.user):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


    def get_fields(self):
        return getattr(settings, USER_FIELD_SETTTING, DEFAULT_USER_FIELDS)

    def get_queryset(self) -> QuerySet[Any]:
        users = super().get_queryset()
        if getattr(settings, 'ACCOUNTS_API_EXCLUDE_SUPERUSERS', True):
            users = users.filter(is_superuser=False)
        if getattr(settings, 'ACCOUNTS_API_EXCLUDE_STAFF', True):
            users = users.filter(is_staff=False)
        return users
