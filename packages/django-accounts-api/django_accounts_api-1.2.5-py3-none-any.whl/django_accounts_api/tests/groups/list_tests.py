from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from django_accounts_api.tests.groups.perms import add_group_permission

User = get_user_model()

test_user_email = "admin@admin.com"

class GroupsTestCase(TestCase):
    '''Basic tests of the groups view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.url = reverse("django_accounts_api:groups")
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.group = Group.objects.create(name="test")
        return super().setUp()

    def test_groups_get_no_auth(self):
        '''An unauthed get should get a 401'''
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_groups_get_no_perms(self):
        '''An authed user with no group permissions should get a 403'''
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 403

    def test_groups_get_with_perms(self):
        '''An authed user with a user permissions gshould get a 200 and a json response'''
        add_group_permission(self.user, 'view')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200
        json = response.json()
        self.assertEqual(len(json), 1)
