from django.utils import timezone
from tests.client import FixturesTestCase
from saas_base.models import Group, Tenant


class TestGroupsAPI(FixturesTestCase):
    tenant_id = 1
    user_id = FixturesTestCase.OWNER_USER_ID

    def test_list_all_groups(self):
        self.force_login()
        resp = self.client.get('/m/groups/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Admin')

    def test_create_group(self):
        self.force_login()
        data = {
            'name': 'Guest',
            'permissions': ['tenant.read'],
        }
        resp = self.client.post('/m/groups/', data=data)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['name'], 'Guest')
        permission = data['permissions'][0]
        self.assertEqual(permission['name'], 'tenant.read')

    def test_expired_tenant_create_group(self):
        tenant = Tenant.objects.create(
            owner_id=self.user_id,
            name='Expired',
            slug='expired',
            expires_at=timezone.now(),
        )
        client = self.client_class()
        client.force_login(self.user)

        client.credentials(
            HTTP_X_TENANT_ID=str(tenant.id),
        )
        data = {
            'name': 'Guest',
            'permissions': ['tenant.read'],
        }
        resp = client.post('/m/groups/', data=data)
        self.assertEqual(resp.status_code, 403)
        data = resp.json()
        self.assertEqual(data['detail'], 'This tenant is expired.')

    def test_retrieve_group(self):
        self.force_login()
        group = Group.objects.filter(tenant=self.tenant_id).first()
        resp = self.client.get(f'/m/groups/{group.id}/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['permissions']), 3)

    def test_update_group_permissions(self):
        self.force_login()
        group = Group.objects.filter(tenant=self.tenant_id).first()
        data = {'permissions': ['tenant.read']}
        resp = self.client.patch(f'/m/groups/{group.id}/', data=data)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['permissions']), 1)

    def test_update_group_name(self):
        self.force_login()
        group = Group.objects.filter(tenant=self.tenant_id).first()
        data = {'name': 'Admin 2'}
        resp = self.client.patch(f'/m/groups/{group.id}/', data=data)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['name'], 'Admin 2')
        self.assertEqual(len(data['permissions']), 3)

    def test_delete_group(self):
        self.force_login()
        group = Group.objects.filter(tenant=self.tenant_id).first()
        resp = self.client.delete(f'/m/groups/{group.id}/')
        self.assertEqual(resp.status_code, 204)
