from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()
test_user_email = "admin@admin.com"


class PasswordResetTestCase(TestCase):
    """Basic tests of the partial HTML password reset view"""

    def setUp(self) -> None:
        """Get the url and create a user"""
        self.url = reverse("django_accounts_api:password_reset")
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        return super().setUp()

    def test_passwordreset_get(self):
        """An unauthed get should get a 200 and a form"""
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert "form" in response.context

    def test_passwordreset_get_json(self):
        """An unauthed get should get a 200 and a form schema """
        response = self.client.get(
            self.url,
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 200
        assert "schema" in response.json()

    def test_passwordreset_post_error(self):
        """An post should get a 400 with a form with errors"""
        response = self.client.post(self.url)
        assert response.status_code == 400
        assert len(response.context["form"].errors) == 1

    def test_passwordreset_post_error_json(self):
        """An post should get a 400 with json with errors"""
        response = self.client.post(
            self.url,
            HTTP_ACCEPT='application/json',
        )
        assert response.status_code == 400
        json = response.json()
        assert len(json['errors']) == 1

    def test_passwordreset_post_ok(self):
        """An post should get a 200"""
        response = self.client.post(
            self.url,
            dict(
                email=test_user_email
            )
        )
        assert response.status_code == 200

    def test_passwordreset_post_ok_json(self):
        """An post should get a 200"""
        response = self.client.post(
            self.url,
            dict(
                email=test_user_email
            ),
            HTTP_ACCEPT='application/json',
        )
        assert response.status_code == 200
