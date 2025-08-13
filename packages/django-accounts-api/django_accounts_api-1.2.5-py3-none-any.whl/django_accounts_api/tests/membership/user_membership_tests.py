from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from django_accounts_api.tests.users_tests import add_user_permission


User = get_user_model()

test_user_email = "admin@admin.com"
test_user_email_2 = "admin2@admin.com"

class UsersMembershipTestCase(TestCase):
    '''Basic tests of the user membership view'''

    def setUp(self) -> None:
        '''Get the url and create a user and a group'''
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.user_2 = User.objects.create_user("test2", password="test", email=test_user_email_2)
        self.group = Group.objects.create(name="test")
        self.group_user_in = Group.objects.create(name="test_2")
        self.url = reverse("django_accounts_api:membership_users")
        self.group_user_in.user_set.add(self.user)
        self.url_single = reverse(
            "django_accounts_api:membership_user",
            kwargs=dict(user_id=self.user.pk)
        )
        self.url_create = reverse(
            "django_accounts_api:membership_user_join",
            kwargs=dict(
                user_id=self.user.pk,
                group_id=self.group.pk
            )
        )
        self.url_create_existing = reverse(
            "django_accounts_api:membership_user_join",
            kwargs=dict(
                user_id=self.user.pk,
                group_id=self.group_user_in.pk
            )
        )
        self.url_create_bad_user = reverse(
            "django_accounts_api:membership_user_join",
            kwargs=dict(
                user_id=9999,
                group_id=self.group.pk
            )
        )
        self.url_create_bad_group = reverse(
            "django_accounts_api:membership_user_join",
            kwargs=dict(
                user_id=self.user.pk,
                group_id=9999
            )
        )
        return super().setUp()

    def test_membership_users_get_no_auth(self):
        '''An unauthed get should get a 401'''
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_membership_users_post_no_auth(self):
        '''An unauthed get should get a 401'''
        response = self.client.post(self.url)
        assert response.status_code == 401

    def test_membership_users_get_no_perms(self):
        '''An authed user with no group permissions should get a 403'''
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 403

    def test_membership_users_post_no_perms(self):
        '''An authed user with no group permissions should get a 403'''
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 403

    def test_membership_users_get_with_perms(self):
        '''An authed user with a user permissions gshould get a 200 and a json response'''
        add_user_permission(self.user, 'view')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200
        json = response.json()
        self.assertDictEqual(json, {'1': [2], '2': []})

    def test_membership_users_single_get_with_perms(self):
        '''An authed user with a user permissions gshould get a 200 and a json response'''
        add_user_permission(self.user, 'view')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url_single,
        )
        assert response.status_code == 200
        json = response.json()
        self.assertDictEqual(json, {'1': [2]})

    def test_membership_users_post_no_perms(self):
        '''An authed user with no user change permission should get a 403'''
        add_user_permission(self.user, 'view')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url_create,
        )
        assert response.status_code == 403

    def test_membership_users_post_no_query_params(self):
        '''An authed user with user change permission should get a 400 if no group id'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 400

    def test_membership_users_post_no_group_param(self):
        '''An authed user with user change permission should get a 400 if no group id'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url_single,
        )
        assert response.status_code == 400

    def test_membership_users_post_no_user_param(self):
        '''An authed user with user change permission should get a 400 if no user id'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 400

    def test_membership_users_post_bad_group(self):
        '''An authed user with user change permission should get a 404 if group id nonexistant'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url_create_bad_group,
        )
        assert response.status_code == 404

    def test_membership_users_post_bad_user(self):
        '''An authed user with user change permission should get a 404 if user id nonexistant'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url_create_bad_user,
        )
        assert response.status_code == 404

    def test_membership_users_post_succeeds(self):
        '''An authed user with user change permission should get a 201 and join the user to the group'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url_create,
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.group.user_set.filter(pk=self.user.pk).exists())

    def test_membership_users_post_existing_succeeds(self):
        '''An authed user with user change permission should get a 201 and join the user to the group'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url_create_existing,
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.group_user_in.user_set.filter(pk=self.user.pk).exists())

    def test_membership_users_delete(self):
        '''An authed user with user change permission should get a 201 and join the user to the group'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.delete(
            self.url_create_existing,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.group_user_in.user_set.filter(pk=self.user.pk).exists())
