from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from django_accounts_api.tests.groups.perms import add_group_permission

User = get_user_model()

test_user_email = "admin@admin.com"


class GroupDeleteTestCase(TestCase):
    '''Basic tests of the group delete view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.group = Group.objects.create(name="test2")
        self.url = reverse("django_accounts_api:group_delete", kwargs={"pk": self.group.pk})
        return super().setUp()

    def test_group_delete_get_no_auth(self):
        '''An unauthed get should receive a 401'''
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_group_delete_get_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 403

    def test_group_delete_post_no_auth(self):
        '''An unauthed post should receive a 401'''
        response = self.client.post(self.url)
        assert response.status_code == 401

    def test_group_delete_post_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 403

    def test_group_delete_get_with_perms(self):
        '''An authed user with a user permissions should get a 200 and a json response'''
        add_group_permission(self.user, 'delete')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200

    def test_group_delete_post_valid(self):
        '''valid details posted should respond with a 200 and delete the user'''
        add_group_permission(self.user, 'delete')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url
        )
        assert response.status_code == 200
        with self.assertRaises(Group.DoesNotExist):
            self.group.refresh_from_db()
