from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class PasswordChangeTestCase(TestCase):
    """Basic tests of the partial HTML password change view"""

    def setUp(self) -> None:
        """Get the url and create a user"""
        self.url = reverse("django_accounts_api:password_change")
        self.user = User.objects.create_user("test", password="test")
        return super().setUp()

    def test_passwordchange_get_unauthed(self):
        """An unauthed get should get a 401"""
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_passwordchange_post_unauthed(self):
        """An unauthed post should get a 401"""
        response = self.client.post(self.url)
        assert response.status_code == 401

    def test_passwordchange_get_authed(self):
        """An authed get should get a 200 and a form"""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert "form" in response.context

    def test_passwordchange_post_authed(self):
        """An authed post should get a 200 witha form with errors"""
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        assert response.status_code == 200
        assert len(response.context["form"].errors) == 3

    def test_passwordchange_post_authed_ok(self):
        """An authed post should get a 200"""
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            dict(
                old_password="test",
                new_password1="newPawThis",
                new_password2="newPawThis"
            )
        )
        assert response.status_code == 200


class APIPasswordChangeTestCase(TestCase):
    """Basic tests of the content type json API change password view"""

    def setUp(self) -> None:
        """Get the url and create a user"""
        self.url = reverse("django_accounts_api:password_change")
        self.user = User.objects.create_user("test", password="test")
        return super().setUp()

    def test_json_passwordchange_get_unauthed(self):
        """An unauthed get with accept json should return a 401"""
        response = self.client.get(
            self.url,
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 401

    def test_json_passwordchange_get_authed(self):
        """An authed get with accept json should return a 200"""
        self.client.force_login(self.user)
        with self.assertRaises(NotImplementedError):
            response = self.client.get(
                self.url,
                HTTP_ACCEPT='application/json'
            )
        # assert response.status_code == 200

    def test_json_passwordchange_post_unauthed(self):
        """An unauthed post with accept json should return a 401"""
        response = self.client.post(
            self.url,
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 401

    def test_json_passwordchange_post_authed_empty_fields(self):
        """An authed post with accept json should return a 400"""
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 400
        response_json = response.json()
        assert len(response_json['errors']) == 3

    def test_json_passwordchange_post_authed_missing_newpass_2(self):
        """An authed post should get a 200"""
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            dict(
                old_password="test",
                new_password1="newPawThis",
            ),
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 400
        response_json = response.json()
        assert len(response_json['errors']) == 1

    def test_json_passwordchange_post_authed_mismatched_newpass_2(self):
        """An authed post should get a 200"""
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            dict(
                old_password="test",
                new_password1="newPawThis",
                new_password2="mismatchedNewPaw",
            ),
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 400
        response_json = response.json()
        assert len(response_json['errors']) == 1


class ChangePasswordFlowTestCase(TestCase):
    """A flow test of the login endpoints"""

    def setUp(self) -> None:
        """Get the url and create a user"""
        self.logout_url = reverse("django_accounts_api:logout")
        self.check_url = reverse("django_accounts_api:login_check")
        self.login_url = reverse("django_accounts_api:login")
        self.cp_url = reverse("django_accounts_api:password_change")
        self.user = User.objects.create_user("test", password="test")
        return super().setUp()

    def test_changepasword_flow(self):
        """ user should be unauthed, login, then be authed, then hit log out, then be unauthed"""
        response = self.client.get(self.check_url)
        assert response.status_code == 401
        response = self.client.post(
            self.login_url, dict(
                username='test',
                password="test"
            ))
        assert response.status_code == 201
        response = self.client.post(
            self.cp_url,
            dict(
                old_password="test",
                new_password1="newPawThis",
                new_password2="newPawThis",
            ),
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 200
        response = self.client.post(self.logout_url)
        assert response.status_code == 200
        response = self.client.post(
            self.login_url, dict(
                username='test',
                password="newPawThis"
            ))
        assert response.status_code == 201
