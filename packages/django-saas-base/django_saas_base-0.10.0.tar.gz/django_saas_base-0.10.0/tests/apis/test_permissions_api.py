from tests.client import FixturesTestCase


class TestPermissionsAPI(FixturesTestCase):
    def test_list_all_permissions(self):
        resp = self.client.get('/m/permissions/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
