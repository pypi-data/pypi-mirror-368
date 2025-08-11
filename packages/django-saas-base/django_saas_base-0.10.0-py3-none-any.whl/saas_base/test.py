import typing as t
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import (
    get_tenant_model,
    Tenant,
    Member,
    Permission,
)


class SaasTestCase(TestCase):
    fixtures = [
        'test_data.yaml',
    ]

    client: APIClient
    client_class = APIClient

    tenant_id: int = 1
    user_id: int = 0

    ADMIN_USER_ID = 1
    STAFF_USER_ID = 2
    OWNER_USER_ID = 3
    GUEST_USER_ID = 4
    EMPTY_USER_ID = 5

    def setUp(self) -> None:
        if self.tenant_id:
            self.client.credentials(
                HTTP_X_TENANT_ID=str(self.tenant_id),
            )

    @property
    def tenant(self):
        return self.get_tenant()

    @property
    def user(self):
        return self.get_user()

    def get_user(self, pk: t.Optional[int] = None) -> User:
        if pk is None:
            pk = self.user_id
        return get_user_model().objects.get(pk=pk)

    def get_tenant(self, pk: t.Optional[int] = None) -> Tenant:
        if pk is None:
            pk = self.tenant_id
        return get_tenant_model().objects.get(pk=pk)

    def get_user_member(self):
        user = self.get_user()
        tenant = self.get_tenant()
        return Member.objects.get(user=user, tenant=tenant)

    def add_user_perms(self, *perms: str):
        member = self.get_user_member()
        for obj in Permission.objects.filter(name__in=perms).all():
            member.permissions.add(obj)
        return member

    def force_login(self, user_id: int = None):
        if user_id is None:
            user = self.get_user()
        else:
            user = self.get_user(user_id)
        self.client.force_login(user)
