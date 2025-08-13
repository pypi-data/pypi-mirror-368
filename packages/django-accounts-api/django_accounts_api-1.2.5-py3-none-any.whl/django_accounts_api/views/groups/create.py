from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.generic.edit import FormView
from django.forms import Form

from django_accounts_api.forms.group import GroupForm
from django_accounts_api.views.accept_json_mixin import AcceptJsonMixin
from django_accounts_api.views.perms import user_has_group_perm


class APIGroupCreate(AcceptJsonMixin, FormView):
    """ Create a group from the basic name
    """
    form_class = GroupForm
    template_name = 'django_accounts_api/form.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        if not user_has_group_perm(request.user, 'add'):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs) -> HttpResponse:
        if self.json_response_requested():
            return JsonResponse(
                [
                    {
                        'type': 'text'
                    }
                ],
                safe=False
            )
        else:
            return super().render_to_response(context, **response_kwargs)

    def form_invalid(self, form: Form) -> HttpResponse:
        if self.json_response_requested():
            response = JsonResponse(
                form.errors
            )
            response.status_code = 400
        else:
            response = super().form_invalid(form)
            response.status_code = 400
        return response


    def form_valid(self, form: Form) -> HttpResponse:
        self.group = form.save()
        return HttpResponse(status=200)
