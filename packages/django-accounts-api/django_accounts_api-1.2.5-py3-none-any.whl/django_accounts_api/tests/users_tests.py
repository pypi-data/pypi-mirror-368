from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

test_user_email = "admin@admin.com"
test_user_email2 = "admin2@admin.com"

def add_user_permission(user: AbstractBaseUser, permission: str):
    user.user_permissions.add(
        Permission.objects.get(
            content_type=ContentType.objects.get_for_model(User),
            codename=f"{permission}_{user._meta.model_name}"
        )
    )


class UsersTestCase(TestCase):
    '''Basic tests of the users view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.url = reverse("django_accounts_api:users")
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        return super().setUp()

    def test_users_get_no_auth(self):
        '''An unauthed get should get a 401'''
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_users_get_no_perms(self):
        '''An authed user with no user permissions gshould get a 403 '''
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 403

    def test_users_get_with_perms(self):
        '''An authed user with a user permissions gshould get a 200 and a json response'''
        add_user_permission(self.user, 'view')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200
        json = response.json()
        self.assertEqual(len(json), 1)


class UserDetailsTestCase(TestCase):
    '''Basic tests of the user details view'''
    def setUp(self) -> None:
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.url = reverse("django_accounts_api:user_details")

    def test_user_detail(self):
        add_user_permission(self.user, 'view')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url
        )
        assert response.status_code == 200


class UserUpdateTestCase(TestCase):
    '''Basic tests of the user update view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.user2 = User.objects.create_user("test2", password="test2", email=test_user_email2)
        self.url = reverse("django_accounts_api:user_update", kwargs={"pk": self.user2.pk})
        return super().setUp()

    def test_user_update_get_no_auth(self):
        '''An unauthed get should receive a 401'''
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_user_update_get_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 403

    def test_user_update_post_no_auth(self):
        '''An unauthed post should receive a 401'''
        response = self.client.post(self.url)
        assert response.status_code == 401

    def test_user_update_post_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 403

    def test_user_update_get_with_perms(self):
        '''An authed user with a user permissions should get a 200 and a json response'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200
        json = response.json()
        self.assertEqual(len(json), 3)

    def test_user_update_post_invalid(self):
        '''Invalid details posted should respond with a 400 '''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                'first_name': 'q' * 200
            }
        )
        assert response.status_code == 400
        json = response.json()
        self.assertEqual(len(json), 1)

    def test_user_update_post_valid(self):
        '''valid details posted should respond with a 200 '''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                'first_name': 'changed1',
                'last_name': 'changed2',
                'email': 'admin3@admin.com',
            }
        )
        assert response.status_code == 200
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.first_name, 'changed1')
        self.assertEqual(self.user2.last_name, 'changed2')
        self.assertEqual(self.user2.email, 'admin3@admin.com')


class UserDeleteTestCase(TestCase):
    '''Basic tests of the user delete view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.user2 = User.objects.create_user("test2", password="test2", email=test_user_email2)
        self.url = reverse("django_accounts_api:user_delete", kwargs={"pk": self.user2.pk})
        return super().setUp()

    def test_user_delete_get_no_auth(self):
        '''An unauthed get should receive a 401'''
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_user_delete_get_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 403

    def test_user_delete_post_no_auth(self):
        '''An unauthed post should receive a 401'''
        response = self.client.post(self.url)
        assert response.status_code == 401

    def test_user_delete_post_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 403

    def test_user_delete_get_with_perms(self):
        '''An authed user with a user permissions should get a 200 and a json response'''
        add_user_permission(self.user, 'delete')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200

    def test_user_delete_post_valid(self):
        '''valid details posted should respond with a 200 and delete the user'''
        add_user_permission(self.user, 'delete')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url
        )
        assert response.status_code == 200
        with self.assertRaises(User.DoesNotExist):
            self.user2.refresh_from_db()


class UserCreateTestCase(TestCase):
    '''Basic tests of the user create view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.url = reverse("django_accounts_api:user_create")
        return super().setUp()

    def test_user_create_get_no_auth(self):
        '''An unauthed get should receive a 401'''
        response = self.client.get(self.url)
        assert response.status_code == 401

    def test_user_create_get_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 403

    def test_user_create_post_no_auth(self):
        '''An unauthed post should receive a 401'''
        response = self.client.post(self.url)
        assert response.status_code == 401

    def test_user_create_post_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 403

    def test_user_create_get_with_perms(self):
        '''An authed user with a user permissions should get a 200 and a json response'''
        add_user_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
        )
        assert response.status_code == 200
        assert 'form' in response.context

    def test_user_create_get_with_perms_json(self):
        '''An authed user with a user permissions should get a 200 and a json response'''
        add_user_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 200
        json = response.json()

    def test_user_create_post_invalid(self):
        '''valid details posted should respond with a 400 and form eith errors'''
        add_user_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            dict(
                username='new user',
            )
        )
        assert response.status_code == 400

    def test_user_create_post_json_invalid(self):
        '''valid details posted should respond with a 400 and form eith errors'''
        add_user_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            dict(
                username='new user',
            ),
            HTTP_ACCEPT='application/json'
        )
        assert response.status_code == 400

    def test_user_create_post_valid(self):
        '''valid details posted should respond with a 200 and create the user'''
        add_user_permission(self.user, 'add')
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            dict(
                username='new_user',
                first_name='New',
                last_name='User',
                email='new@user.com'
            )
        )
        assert response.status_code == 200
        new_user: AbstractBaseUser = User.objects.get(username='new_user')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'User')
        self.assertEqual(new_user.email, 'new@user.com')
        self.assertFalse(new_user.has_usable_password())
        self.assertEqual(len(mail.outbox), 1)

class UserResetPasswordTestCase(TestCase):
    '''Basic tests of the user reset password view'''

    def setUp(self) -> None:
        '''Get the url and create a user'''
        self.user = User.objects.create_user("test", password="test", email=test_user_email)
        self.not_found_url = reverse("django_accounts_api:user_reset", kwargs=dict(pk=999999))
        self.url = reverse("django_accounts_api:user_reset", kwargs=dict(pk=self.user.id))
        return super().setUp()


    def test_user_reset_post_no_auth(self):
        '''An unauthed post should receive a 401'''
        response = self.client.post(self.url)
        assert response.status_code == 401

    def test_user_create_post_no_perms(self):
        '''An authed user with no user permissions should receive a 403 '''
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        assert response.status_code == 403

    def test_user_reset_get_not_supported(self):
        '''An unauthed post should receive a method not supported'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 405

    def test_user_reset_post_non_existant(self):
        '''An authed post to a non-existant user should receive a not found'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(self.not_found_url)
        assert response.status_code == 404

    def test_user_reset_post(self):
        '''An authed post should reset the user password'''
        add_user_permission(self.user, 'change')
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        assert response.status_code == 200
        self.assertEqual(len(mail.outbox), 1)
