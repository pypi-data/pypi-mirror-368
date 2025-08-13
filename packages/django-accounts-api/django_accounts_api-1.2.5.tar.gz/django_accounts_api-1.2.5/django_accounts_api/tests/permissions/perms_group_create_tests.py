from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django_accounts_api.tests.groups.perms import add_group_permission

from django_accounts_api.tests.users_tests import add_user_permission

User = get_user_model()

test_user_email = "admin@admin.com"


class PermissionsGroupCreateTestCase(TestCase):
    '''Basic tests of the group permission create view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.group = Group.objects.create(name="test")
        self.view_group_perm = Permission.objects.get(
            content_type__app_label='auth',
            codename = 'add_group'
        )
        self.url = reverse(
            "django_accounts_api:group_permission_create",
            kwargs=dict(
                group_id=self.group.pk,
                permission_id=self.view_group_perm.pk
            ))
        #self.group.permissions.add(self.view_group_perm)
        return super().setUp()

    def test_create_get(self):
        '''A get should get a 405'''
        response = self.client.get(self.url)
        assert response.status_code == 405

    def test_create_no_perms(self):
        '''An authed user with no group permissions should get a 403'''
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 403

    def test_create_with_group_perms(self):
        '''An authed user with a user permission should get a 200 and a json response'''
        add_group_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 201
        perms = self.group.permissions.all()
        self.assertEqual(perms.count(), 1)

    def test_create_with_user_perms(self):
        '''An authed user with a group permission should get a 200 and a json response'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        self.assertEqual(response.status_code, 403)
