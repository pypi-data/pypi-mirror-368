from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from saas_base.models import get_tenant_model


class TestMembersAPI(TestCase):
    fixtures = [
        'test_data.yaml',
    ]
    client: APIClient
    client_class = APIClient

    tenant_id = 1
    user_id = 3

    def get_user(self):
        return get_user_model().objects.get(pk=self.user_id)

    @property
    def tenant(self):
        return get_tenant_model().objects.get(pk=self.tenant_id)

    def test_list_users_via_owner(self):
        self.client.force_login(self.get_user())
        resp = self.client.get(f'/tenant/{self.tenant_id}/members/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['count'], 2)
