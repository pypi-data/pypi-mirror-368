from saas_base.test import SaasTestCase


class TestUserPasswordAPI(SaasTestCase):
    user_id = SaasTestCase.OWNER_USER_ID

    def prepare_user(self):
        user = self.get_user()
        user.set_password('test')
        user.save()

    def send_request(self, data):
        self.force_login()
        url = '/m/user/password/'
        return self.client.post(url, data=data, format='json')

    def test_update_password(self):
        self.prepare_user()
        data = {'old_password': 'test', 'password': 'abc12.3D', 'confirm_password': 'abc12.3D'}
        resp = self.send_request(data)
        self.assertEqual(resp.status_code, 204)

    def test_not_match_password(self):
        self.prepare_user()
        data = {'old_password': 'test', 'password': 'abc12.3D', 'confirm_password': 'abc12.3C'}
        resp = self.send_request(data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['password'], ['Password does not match.'])

    def test_too_simple_password(self):
        self.prepare_user()
        data = {'old_password': 'test', 'password': 'foo', 'confirm_password': 'foo'}
        resp = self.send_request(data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            resp.json()['password'], ['This password is too short. It must contain at least 8 characters.']
        )

    def test_missing_fields(self):
        self.prepare_user()
        data = {'old_password': 'test'}
        resp = self.send_request(data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['password'], ['This field is required.'])

        data = {'password': 'abc12.3D', 'confirm_password': 'abc12.3D'}
        resp = self.send_request(data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['old_password'], ['This field is required.'])

    def test_invalid_old_password(self):
        self.prepare_user()
        data = {'old_password': 'invalid', 'password': 'abc12.3D', 'confirm_password': 'abc12.3D'}
        resp = self.send_request(data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['old_password'], ['Password incorrect.'])
