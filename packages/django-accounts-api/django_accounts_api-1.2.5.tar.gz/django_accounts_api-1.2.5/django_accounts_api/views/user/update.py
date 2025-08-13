from django.contrib.auth import get_user_model
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.generic.edit import UpdateView

from django_accounts_api.views.perms import user_has_user_perm

User = get_user_model()


class APIUserUpdate(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email', 'is_active']
    template_name = 'django_accounts_api/schemas/user_update.json'
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not user_has_user_perm(request.user, 'change'):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        response = JsonResponse(form.errors)
        response.status_code = 400
        return response

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.save()
        return HttpResponse(status=200)

    def render_to_response(self, context, **response_kwargs) -> HttpResponse:
        response = super().render_to_response(context, **response_kwargs)
        response['Content-Type'] = 'application/json'
        return response
