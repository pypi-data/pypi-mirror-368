from django.test import TestCase
from django.urls import reverse


class ManifestTestCase(TestCase):
    """Basic tests of the manifest"""

    def setUp(self) -> None:
        """Get the url and create a user"""
        self.url = reverse("django_accounts_api:manifest")
        return super().setUp()

    def test_get_manifest(self):
        """An unauthed get should get a 200 with a form"""
        response = self.client.get(self.url)
        assert response.status_code == 200
        json = response.json()
        assert "login" in json
        assert "logout" in json
        assert "password_change" in json
        assert "password_reset" in json
        assert "password_reset_confirm" in json
        assert "users" in json
        assert "user_create" in json
        assert "user_update" in json
        assert "user_delete" in json
        assert "user_reset" in json
