from tests.client import FixturesTestCase


class TestRolesAPI(FixturesTestCase):
    def test_list_all_roles(self):
        resp = self.client.get('/m/roles/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        role_names = [d['name'] for d in data]
        self.assertIn('admin', role_names)
