from django.contrib.auth.views import LogoutView
from django.http import HttpResponse


class APILogout(LogoutView):
    ''' Override the Django logout view to NOT redirect on successful login

    POST - logs out, returns 200
    '''

    def post(self, request, *args, **kwargs):
        _repressed_redirect_or_render = super().post(request, *args, **kwargs)  # noqa: F841
        return HttpResponse(
            status=200
        )
