from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.views import View


class APIManifest(View):
    """Return a json encoded dictionary {name: path} for views offered
    by Django Accounts API
    """

    def get(self, request, *args, **kwargs):
        return JsonResponse(dict(
            login=reverse("django_accounts_api:login"),
            logout=reverse("django_accounts_api:logout"),
            password_change=reverse("django_accounts_api:password_change"),
            password_reset=reverse("django_accounts_api:password_reset"),
            password_reset_confirm=reverse(
                "django_accounts_api:password_reset_confirm",
                kwargs=dict(uidb64="uidb64", token="token")
            ),

            users=reverse("django_accounts_api:users"),
            user_create=reverse("django_accounts_api:user_create"),
            user_update=reverse(
                "django_accounts_api:user_update",
                kwargs=dict(pk=00000)
            ),
            user_delete=reverse(
                "django_accounts_api:user_delete",
                kwargs=dict(pk=00000)
            ),
            user_reset=reverse(
                "django_accounts_api:user_reset",
                kwargs=dict(pk=00000)
            ),
            user_details=reverse("django_accounts_api:user_details"),
        ))
