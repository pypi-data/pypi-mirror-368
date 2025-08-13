from django.contrib.auth.models import User as DjangoUser
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from django_accounts_api.views.user_details import user_details


@method_decorator(never_cache, name='get')
class APILoginCheck(View):
    """
    200 and details if logged in, 401 if not

    User details are basic, but can be expanded by providing a dotted import path to a
    function returning a json serializable dict from the user parameter
    """

    def get(self, request, *args, **kwargs):
        user: DjangoUser = request.user
        if (user.is_authenticated):
            return JsonResponse(user_details(user))
        else:
            return HttpResponse(status=401)
