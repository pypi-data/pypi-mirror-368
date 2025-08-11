from django.core import mail
from saas_base.models import UserEmail
from tests.client import FixturesTestCase


class TestEmailAPI(FixturesTestCase):
    user_id = FixturesTestCase.EMPTY_USER_ID

    def test_list_emails(self):
        self.force_login()

        url = '/m/user/emails/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

        for i in range(5):
            UserEmail.objects.create(user=self.user, email=f'demo-{self.user_id}-{i}@example.com')

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 5)

    def test_add_email(self):
        self.force_login()
        data1 = {'email': 'demo-1-1@example.com'}
        resp = self.client.post('/m/user/emails/add/request/', data1)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)

        data2 = {**data1, 'code': self.get_mail_auth_code()}
        resp = self.client.post('/m/user/emails/add/confirm/', data=data2)
        self.assertEqual(resp.status_code, 200)
        item = resp.json()

        url = '/m/user/emails/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [item])

    def test_set_primary_email(self):
        self.force_login()

        obj = UserEmail.objects.create(
            user=self.user,
            email='demo-1-2@example.com',
            verified=True,
        )
        url = f'/m/user/emails/{obj.pk}/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['primary'])

        resp = self.client.patch(url, data={'primary': True})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['primary'])

    def test_delete_email(self):
        self.force_login()
        obj = UserEmail.objects.create(
            user=self.user,
            email='demo-1-2@example.com',
            verified=True,
        )
        url = f'/m/user/emails/{obj.pk}/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(UserEmail.objects.filter(user=self.user).count(), 0)
