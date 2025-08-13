from django.contrib.auth.views import PasswordChangeView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls.exceptions import NoReverseMatch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from django_accounts_api.views.accept_json_mixin import AcceptJsonMixin


@method_decorator(sensitive_post_parameters(), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class APIPasswordChange(AcceptJsonMixin, PasswordChangeView):
    ''' Override the Django change password view to support API use

    GET:

    - default: renders a partial change password form
    - json requested: TODO - Not Implemented yet - json form schema?

    POST - success: 200, failure: 400

    - default: renders a password form with errors
    - json requested: returns password form errors
    '''
    template_name = "django_accounts_api/form.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        """Django's PasswordChangeView is login required and redirects, we suppress this and 401"""
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        """Override the get behavior if json requested TODO json schema"""
        if request.user.is_authenticated:
            if (self.json_response_requested()):
                raise NotImplementedError()
            else:
                return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        """Override redirect behavior if json is requested return json errors"""
        if self.json_response_requested():
            return JsonResponse(dict(errors=form.errors), status=400)
        else:
            return super().form_invalid(form)

    def form_valid(self, form):
        """Override redirect behavior just return 200 OK"""
        try:
            _repressed_redirect = super().form_valid(form)  # noqa: F841
        except NoReverseMatch:
            pass
        return HttpResponse(status=200)
