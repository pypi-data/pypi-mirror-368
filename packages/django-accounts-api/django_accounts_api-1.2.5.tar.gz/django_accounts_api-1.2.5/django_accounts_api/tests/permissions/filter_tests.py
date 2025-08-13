from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.test import TestCase

from django_accounts_api.views.permissions.permissions_filter import PermissionFilter, combine_filters

User = get_user_model()


class PermissionsFilterTestCase(TestCase):
    '''Basic tests of the permission filters'''

    def test_single_model(self):
        '''A single model provided should return all 4 permissions'''
        pf = PermissionFilter(Group, None)
        q = pf.permissionQ()
        perms = Permission.objects.filter(q)
        self.assertEqual(perms.count(), 4)

    def test_perms_list(self):
        '''A perms list provided should return those permissions'''
        pf = PermissionFilter(User, ('add_user', 'view_user'))
        q = pf.permissionQ()
        perms = Permission.objects.filter(q)
        self.assertEqual(perms.count(), 2)

    def test_perms_combination(self):
        '''A perms list provided should return those permissions'''
        pf_1 = PermissionFilter(Group, None)
        pf_2 = PermissionFilter(User, ('add_user', 'view_user'))
        pf_combined = combine_filters((pf_1, pf_2))
        perms = Permission.objects.filter(pf_combined)
        self.assertEqual(perms.count(), 6)
