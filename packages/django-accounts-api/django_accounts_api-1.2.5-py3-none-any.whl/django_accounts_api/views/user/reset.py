from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from django_accounts_api.views.reset_password_mixin import ResetPasswordMixin
from django_accounts_api.views.perms import user_has_user_perm

User = get_user_model()


class APIUserReset(SingleObjectMixin, ResetPasswordMixin, View):
    model = User
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not user_has_user_perm(request.user, 'change'):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.user = self.get_object()
        self.set_reset_link(self.user)
        return HttpResponse(self.reset_link, status=200)
