from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    INTERNAL_RESET_SESSION_TOKEN
)

User = get_user_model()
test_user_email = "admin@admin.com"


class PasswordResetTestCase(TestCase):
    """Basic tests of the partial HTML password reset view"""

    def setUp(self) -> None:
        """Get the url and create a user"""
        self.user = User.objects.create_user(
            "test", password="test", email=test_user_email
        )
        self.valid_token = default_token_generator.make_token(self.user)
        self.reset_url_token = 'set-password'
        self.email_url_bad_user = reverse(
            "django_accounts_api:password_reset_confirm",
            kwargs=dict(
                uidb64=urlsafe_base64_encode(force_bytes('nonexistant')),
                token=self.valid_token
            )
        )
        self.email_url = reverse(
            "django_accounts_api:password_reset_confirm",
            kwargs=dict(
                uidb64=urlsafe_base64_encode(force_bytes(self.user.pk)),
                token=default_token_generator.make_token(self.user)
            )
        )
        self.email_invalid_token_url = reverse(
            "django_accounts_api:password_reset_confirm",
            kwargs=dict(
                uidb64=urlsafe_base64_encode(force_bytes(self.user.pk)),
                token="invalid_token"
            )
        )
        self.reset_url = reverse(
            "django_accounts_api:password_reset_confirm",
            kwargs=dict(
                uidb64=urlsafe_base64_encode(force_bytes(self.user.pk)),
                token=self.reset_url_token
            )
        )
        return super().setUp()

    def set_token_in_session(self):
        # Set the session token - must set as variable and call save!
        session = self.client.session
        session[INTERNAL_RESET_SESSION_TOKEN] = self.valid_token
        session.save()

    @override_settings(
        ROOT_URLCONF='testproject.urls_reset_misconfigured'
    )
    def test_password_reset_confirm_misconfigured(self):
        ''' Should return 400 invalid token '''
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(
                '/api/bad'
            )

    def test_password_reset_confirm_bad_user(self):
        ''' Should redirect to the frontend invalid reset code page '''
        response = self.client.get(
            self.email_url_bad_user
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], '/reset-password/invalid')

    def test_password_reset_confirm_invalid_code_get(self):
        ''' Should redirect to the frontend invalid reset code page '''
        response = self.client.get(
            self.email_invalid_token_url
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], '/reset-password/invalid')

    @override_settings(
        ACCOUNTS_API_RESET_REDIRECT_INVALID='/test'
    )
    def test_password_reset_confirm_invalid_code_get_obeys_setting(self):
        ''' Should redirect to the frontend invalid reset code page '''
        response = self.client.get(
            self.email_invalid_token_url
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], '/test')

    def test_password_reset_confirm_valid_get(self):
        ''' Should redirect to the frontend reset password page, placing the token in the sesssion'''
        response = self.client.get(
            self.email_url,
        )
        self.assertEqual(response.status_code, 302)
        location = response.headers["Location"]
        self.assertTrue(location.startswith('/reset-password/'))
        session_token = self.client.session.get(INTERNAL_RESET_SESSION_TOKEN)
        self.assertEqual(session_token, self.valid_token)

    @override_settings(
        ACCOUNTS_API_RESET_REDIRECT='/test/'
    )
    def test_password_reset_confirm_valid_get_obeys_settings(self):
        ''' Should redirect to the frontend reset password page, placing the token in the sesssion'''
        response = self.client.get(
            self.email_url,
        )
        self.assertEqual(response.status_code, 302)
        location = response.headers["Location"]
        self.assertTrue(location.startswith('/test/'))
        session_token = self.client.session.get(INTERNAL_RESET_SESSION_TOKEN)
        self.assertEqual(session_token, self.valid_token)

    def test_password_reset_confirm_post_success(self):
        data = {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
        }

        self.set_token_in_session()

        session = self.client.session
        session[INTERNAL_RESET_SESSION_TOKEN] = self.valid_token
        session.save()

        response = self.client.post(
            self.reset_url, data,
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    @override_settings(
        ACCOUNTS_API_RESET_LOGIN=True
    )
    def test_password_reset_confirm_post_success_login(self):
        data = {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
        }

        self.set_token_in_session()

        response = self.client.post(
            self.reset_url, data,
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_password_reset_confirm_post_form_invalid(self):
        data = {
            'new_password1': 'newpass123',
            'new_password2': 'not_good',
        }

        self.set_token_in_session()

        response = self.client.post(
            self.reset_url, data,
        )
        self.assertEqual(response.status_code, 400)
        assert "form" in response.context
        self.assertEqual(len(response.context['form'].errors), 1)

    def test_password_reset_confirm_post_form_invalid_json(self):
        data = {
            'new_password1': 'newpass123',
            'new_password2': 'not_good',
        }

        self.set_token_in_session()

        response = self.client.post(
            self.reset_url, data,
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 400)
        responseContent = response.json()
        self.assertEqual(len(responseContent['errors']), 1)

    '''
    def test_password_reset_confirm_post_no_token(self):
        # prepare the data with invalid token
        data = {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
        }
        response = self.client.post(
            self.reset_url, data,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.status_text, 'invalid request')
    '''
