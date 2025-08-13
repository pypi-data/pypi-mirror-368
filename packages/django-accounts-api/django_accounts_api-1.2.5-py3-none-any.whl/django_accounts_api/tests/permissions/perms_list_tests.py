from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django_accounts_api.tests.groups.perms import add_group_permission

from django_accounts_api.tests.users_tests import add_user_permission

User = get_user_model()

test_user_email = "admin@admin.com"


class PermissionsListTestCase(TestCase):
    '''Basic tests of the permission list view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.url = reverse("django_accounts_api:permissions")
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.group = Group.objects.create(name="test")
        self.view_group_perm = Permission.objects.get(
            content_type__app_label='auth',
            codename = 'add_group'
        )
        self.group.permissions.add(self.view_group_perm)
        return super().setUp()

    def test_permissions_get_no_auth(self):
        '''An unauthed get should get a 401'''
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_permissions_get_no_perms(self):
        '''An authed user with no group permissions should get a 403'''
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 403

    def test_permissions_get_with_user_perms(self):
        '''An authed user with a user permission should get a 200 and a json response'''
        add_user_permission(self.user, 'view')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200
        json = response.json()
        permissions = json['permissions']
        user_perms = json['user_perms']
        self.assertEqual(len(permissions), 8)
        self.assertEqual(len(user_perms), 1)

    def test_permissions_get_with_group_perms(self):
        '''An authed user with a group permission should get a 200 and a json response'''
        add_group_permission(self.user, 'view')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200
        json = response.json()
        permissions = json['permissions']
        group_perms = json['group_perms']
        self.assertEqual(len(group_perms), 1)
        self.assertEqual(len(permissions), 8)
