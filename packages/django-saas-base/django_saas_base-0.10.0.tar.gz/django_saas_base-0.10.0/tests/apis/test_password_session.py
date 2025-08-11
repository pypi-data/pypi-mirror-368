import re
from django.core import mail
from tests.client import FixturesTestCase
from saas_base.models import UserEmail


class TestPasswordAPI(FixturesTestCase):
    user_id = FixturesTestCase.OWNER_USER_ID

    def setUp(self):
        user = self.get_user()
        UserEmail.objects.create(user=user, email='hi@foo.com', primary=True, verified=True)

    def test_reset_password(self):
        data = {'email': 'hi@foo.com'}
        resp = self.client.post('/m/session/password/forgot/', data=data)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        codes = re.findall(r'Code: (\w{6})', msg.body)

        data = {**data, 'code': codes[0], 'password': 'this is me'}
        resp = self.client.post('/m/session/password/reset/', data=data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('next', resp.json())

    def test_wrong_email(self):
        data = {'email': '404@foo.com'}
        resp = self.client.post('/m/session/password/forgot/', data=data)
        self.assertEqual(resp.status_code, 400)

    def test_wrong_code(self):
        data = {'email': 'hi@foo.com'}
        resp = self.client.post('/m/session/password/forgot/', data=data)
        self.assertEqual(resp.status_code, 204)
        data = {**data, 'code': 'AAAAAA', 'password': 'this is me'}
        resp = self.client.post('/m/session/password/reset/', data=data)
        self.assertEqual(resp.status_code, 400)
