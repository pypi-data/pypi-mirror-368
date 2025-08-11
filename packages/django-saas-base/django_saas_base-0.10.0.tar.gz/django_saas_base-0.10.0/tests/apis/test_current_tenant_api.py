from tests.client import FixturesTestCase


class TestCurrentTenantAPI(FixturesTestCase):
    user_id = FixturesTestCase.OWNER_USER_ID

    def test_fetch_demo_tenant(self):
        self.force_login()
        resp = self.client.get('/m/tenant/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['slug'], self.tenant.slug)

    def test_current_membership(self):
        self.force_login()
        resp = self.client.get('/m/tenant/member/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'active')
