from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN, PasswordResetConfirmView, PasswordResetView
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls.exceptions import NoReverseMatch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from django_accounts_api.views.accept_json_mixin import AcceptJsonMixin
from django_accounts_api.views.form_template_mixin import ConfigurableFormTemplateResponseMixin


@method_decorator(sensitive_post_parameters(), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class APIPasswordResetView(AcceptJsonMixin, ConfigurableFormTemplateResponseMixin, PasswordResetView):
    ''' Override the Django password reset view to support API use

    GET:

    - default: renders a partial password reset form
    - if header Accept: application/json set return a login json form schema

    POST - success: sends a password reset email, returns 200

    POST - failure: 400

    - default: renders a partial password reset form with errors
    - if header Accept: application/json set password reset form errors
    '''
    email_template_name = "django_accounts_api/password_reset_email.html"
    html_email_template_name = "django_accounts_api/password_reset_email_html.html"
    subject_template_name = "django_accounts_api/password_reset_subject.txt"

    def get(self, request, *args, **kwargs):
        """Override the get behavior if json requested return json schema"""
        if self.json_response_requested():
            return JsonResponse({
                'schema': [
                    dict(
                        type="email",
                        name="email",
                        label="Email address",
                        help="Please enter your email address.",
                        validation="required|email",
                        placeholder="enter your email",
                    )
                ]})
        else:
            return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        """Override redirect behavior to return 400
        if json is requested return json errors
        """
        if self.json_response_requested():
            return JsonResponse(dict(errors=form.errors), status=400)
        else:
            response = super().form_invalid(form)
            response.status_code = 400
            return response

    def form_valid(self, form):
        """Override form_valid method to return 200 OK"""
        try:
            _repressed_redirect = super().form_valid(form)  # noqa: F841
        except NoReverseMatch:
            pass
        return HttpResponse(status=200)


@method_decorator(csrf_protect, name='dispatch')
class APIPasswordResetConfirmView(AcceptJsonMixin, PasswordResetConfirmView):
    ''' Override the Django password reset confirm view to support API use

    GET:

    - validates and stores token in session just like django base view
    - validation success redirects to a configured non-django URL default '/reset-password/'
    - validation failure redirects to a configurable non-django URL default '/reset-password/invalid/'

    POST - success: 200, failure: 400

    - default: renders a partial password reset confirm form with errors
    - if header Accept: application/json set returns password reset confirm form errors
    '''
    def __init__(self, **kwargs) -> None:
        # We read password change post login settings to control whether the user is logged in
        # on successful password change
        if 'post_reset_login' not in kwargs:
            kwargs['post_reset_login'] = getattr(
                settings,
                'ACCOUNTS_API_RESET_LOGIN',
                False
            )
        if 'post_reset_login_backend' not in kwargs:
            kwargs['post_reset_login_backend'] = getattr(
                settings,
                'ACCOUNTS_API_RESET_LOGIN_BACKEND',
                None
            )
        # Read the frontend reset paths from the settings
        self.reset_redirect = getattr(
            settings,
            'ACCOUNTS_API_RESET_REDIRECT',
            '/reset-password/'
        )
        self.reset_invalid_redirect = getattr(
            settings,
            'ACCOUNTS_API_RESET_REDIRECT_INVALID',
            '/reset-password/invalid'
        )

        super().__init__(**kwargs)

    template_name = 'django_accounts_api/form.html'

    def dispatch(self, *args, **kwargs) -> HttpResponse:
        ''' Code duplicated from django/contrib/auth/views.PasswordResetConfirmView.dispatch
        We need to change this to redirect to the frontend ( where marked - Django Accounts API Change )
        '''
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    # Django Accounts API Change Start
                    # Redirects the user to the frontend for the password change form
                    redirect_url = f'{self.reset_redirect}{kwargs["uidb64"]}/{self.reset_url_token}'                    #
                    # Django Accounts API Change End
                    return HttpResponseRedirect(redirect_url)

        # Django Accounts API Change Start
        return self.invalid_code()
        # Django Accounts API Change End

    def invalid_code(self):
        ''' Redirect to the frontend invliad code path
        '''
        return HttpResponseRedirect(self.reset_invalid_redirect)

    def form_valid(self, form):
        """
        If the form is valid, duplicate django's code, avoiding
        reversing the password_reset_complete url which may not exist
        """
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)

        response =  HttpResponse(status=200)
        response.reason_phrase='password reset confirmed'
        return response

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        if self.json_response_requested():
            response = JsonResponse({'errors': form.errors}, status=400)
        else:
            response = super().form_invalid(form)
            response.status_code = 400
        return response
