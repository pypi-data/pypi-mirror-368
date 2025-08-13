from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from django_accounts_api.tests.groups.perms import add_group_permission

User = get_user_model()

test_user_email = "admin@admin.com"
test_user_email_2= "admin2@admin.com"

class GroupsMembershipTestCase(TestCase):
    '''Basic tests of the group membership view'''

    def setUp(self) -> None:
        '''Get the url and create a user and a group'''
        self.group = Group.objects.create(name="test")
        self.url = reverse("django_accounts_api:membership_groups")
        self.url_single = reverse("django_accounts_api:membership_group", kwargs=dict(group_id=self.group.pk))
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.user_2 = User.objects.create_user("test_2", password="test", email=test_user_email_2)
        self.group_2 = Group.objects.create(name="test_2")
        self.group.user_set.add(self.user)
        self.group_2.user_set.add(self.user_2)
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
        self.assertDictEqual(json, {'1': [1], '2': [2]})

    def test_group_single_get_with_perms(self):
        '''An authed user with a user permissions gshould get a 200 and a json response'''
        add_group_permission(self.user, 'view')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url_single,
        )
        assert response.status_code == 200
        json = response.json()
        self.assertDictEqual(json, {'1': [1]})
