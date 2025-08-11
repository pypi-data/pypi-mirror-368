from saas_base.models import Member, Permission, Group
from saas_base.models import get_tenant_model
from saas_base.test import SaasTestCase


class TestTenantsAPI(SaasTestCase):
    user_id = SaasTestCase.EMPTY_USER_ID

    def test_list_tenants(self):
        self.force_login()
        user = self.get_user()

        tenants = create_demo_tenants(count=2)
        for tenant in tenants:
            Member.objects.create(
                user=user,
                tenant=tenant,
                status=Member.InviteStatus.WAITING,
            )

        url = '/m/user/members/?status=all'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['count'], 2)

        url = '/m/user/members/?status=waiting'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['count'], 2)

        url = '/m/user/members/?status=active'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['count'], 0)

    def test_list_tenant_flat_permissions(self):
        self.force_login()
        user = self.get_user()
        tenants = create_demo_tenants(count=2)

        members = []
        for tenant in tenants:
            member = Member.objects.create(
                user=user,
                tenant=tenant,
                status=Member.InviteStatus.ACTIVE,
            )
            members.append(member)
            member.permissions.add(Permission.objects.get_by_name('tenant.read'))

        group = Group.objects.create(tenant=tenants[0], name='Admin')
        group.permissions.add(Permission.objects.get_by_name('tenant.admin'))
        members[0].groups.add(group)

        group = Group.objects.create(tenant=tenants[1], name='Guest')
        members[1].groups.add(group)

        url = '/m/user/members/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 2)


def create_demo_tenants(prefix: str = 'demo', region: str = 'us', count: int = 10):
    tenants = []
    for i in range(count):
        tenant = get_tenant_model().objects.create(slug=f'{prefix}-0{i}', region=region)
        tenants.append(tenant)
    return tenants
