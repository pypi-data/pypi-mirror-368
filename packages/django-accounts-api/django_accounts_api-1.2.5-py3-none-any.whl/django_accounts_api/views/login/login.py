from http import HTTPStatus

from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters

from django_accounts_api.views.accept_json_mixin import AcceptJsonMixin
from django_accounts_api.views.form_template_mixin import ConfigurableFormTemplateResponseMixin
from django_accounts_api.views.user_details import user_details


@method_decorator(ensure_csrf_cookie, name='get')
@method_decorator(sensitive_post_parameters(), name='dispatch')
class APILogin(AcceptJsonMixin, ConfigurableFormTemplateResponseMixin, LoginView):
    '''
    Override the Django login view to be API friendly for json or partial html

    GET:

    - default: renders a partial login form
    - if header Accept: application/json set returns a json form schema

    POST success: logs the user in, returns 200 OK

    POST failure: 400

    - default: renders a password form with errors
    - if header Accept: application/json set returns password form errors

    '''

    def form_valid(self, form):
        """Override redirect behavior to return JSON user details"""
        _repressed_redirect = super().form_valid(form)  # noqa: F841
        return JsonResponse(
            user_details(self.request.user),
            status=201
        )

    def form_invalid(self, form):
        """Override redirect behavior if json is requested return json errors"""
        if self.json_response_requested():
            return JsonResponse(dict(errors=form.errors), status=400)
        else:
            return super().form_invalid(form)

    def get(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        """Override the get behavior if json requested return user details"""
        if self.json_response_requested():
            if (request.user.is_authenticated):
                return JsonResponse(user_details(request.user))
            else:
                return JsonResponse({}, status=HTTPStatus.NO_CONTENT)
        else:
            return super().get(request, *args, **kwargs)
