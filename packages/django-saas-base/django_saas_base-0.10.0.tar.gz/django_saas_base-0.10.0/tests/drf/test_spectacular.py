from saas_base.test import SaasTestCase


class TestCurrentTenantAPI(SaasTestCase):
    def test_fetch_openapi(self):
        resp = self.client.get('/schema/openapi')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('openapi', resp.json())
