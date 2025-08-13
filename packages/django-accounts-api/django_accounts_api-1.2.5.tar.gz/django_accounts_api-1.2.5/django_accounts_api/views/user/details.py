from django_accounts_api.views.user_details import user_details
from django.views import View
from django.http import JsonResponse


class UserDetails(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(user_details(request.user))
