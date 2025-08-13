from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.views.generic.edit import DeleteView

from django_accounts_api.views.perms import user_has_group_perm


class APIGroupDelete(DeleteView):
    model = Group

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not user_has_group_perm(request.user, 'delete'):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse:
        self.object.delete()
        return HttpResponse(status=200)

    def render_to_response(self, context, **response_kwargs) -> HttpResponse:
        return HttpResponse(status=200)
