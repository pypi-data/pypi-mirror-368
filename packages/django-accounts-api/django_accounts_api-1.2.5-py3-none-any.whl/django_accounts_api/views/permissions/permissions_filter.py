from typing import Iterable
from django.db.models import Q, Model


class PermissionFilter(object):
    ''' a instance of a permission filter'''
    model: Model = None
    permissions = None

    def __init__(self, model: Model, permissions=None):
        self.model = model
        self.permissions = permissions

    def permissionQ(self):
        model_Q = Q(
            content_type__app_label=self.model._meta.app_label,
            content_type__model=self.model._meta.model_name
        ) if self.model else None
        permissions_Q = Q(codename__in=self.permissions) if self.permissions else None
        if self.model and self.permissions:
            return Q(model_Q & permissions_Q)
        if self.model:
            return model_Q
        if self.permissions:
            return permissions_Q


def combine_filters(filters: Iterable[PermissionFilter]):
    q = Q()
    for f in filters:
        q = q | f.permissionQ()
    return q
