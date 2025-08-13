from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from django_accounts_api.tests.groups.perms import add_group_permission

User = get_user_model()

test_user_email = "admin@admin.com"

class GroupCreateTestCase(TestCase):
    '''Basic tests of the user create view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.url = reverse("django_accounts_api:group_create")
        return super().setUp()

    def test_group_create_get_no_auth(self):
        '''An unauthed get should receive a 401'''
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_group_create_get_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 403

    def test_group_create_post_no_auth(self):
        '''An unauthed post should receive a 401'''
        response = self.client.post(self.url)
        assert response.status_code == 401

    def test_group_create_post_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 403

    def test_group_create_get_with_perms(self):
        '''An authed user with a user permissions should get a 200 and a json response'''
        add_group_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200
        assert 'form' in response.context

    def test_group_create_get_with_perms_json(self):
        '''An authed user with a user permissions should get a 200 and a json response'''
        add_group_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 200
        json = response.json()

    def test_group_create_post_invalid(self):
        '''invalid details posted should respond with a 400 and form eith errors'''
        add_group_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            dict(
                name='new group' * 50,
            )
        )
        assert response.status_code == 400
        self.assertEqual(Group.objects.all().count(), 0)

    def test_group_create_post_json_invalid(self):
        '''valid details posted should respond with a 400 and form eith errors'''
        add_group_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            dict(
                name='new group' * 50,
            ),
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 400

    def test_group_create_post_valid(self):
        '''valid details posted should respond with a 200 and create the user'''
        add_group_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            dict(
                name='new_group',
            )
        )
        assert response.status_code == 200
        self.assertEqual(Group.objects.all().count(), 1)
