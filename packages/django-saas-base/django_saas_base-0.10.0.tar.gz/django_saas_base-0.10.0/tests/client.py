import os
import re
import json
from django.core import mail
from saas_base.test import SaasTestCase
from requests_mock import Mocker

ROOT = os.path.dirname(__file__)


class FixturesTestCase(SaasTestCase):
    @staticmethod
    def get_mail_auth_code():
        msg = mail.outbox[0]
        codes = re.findall(r'Code: (\w{6})', msg.body)
        return codes[0]

    @staticmethod
    def load_fixture(name: str):
        filename = os.path.join(ROOT, 'fixtures', name)
        with open(filename) as f:
            data = json.load(f)
        return data

    @classmethod
    def mock_requests(cls, *names: str):
        m = Mocker()
        for name in names:
            data = cls.load_fixture(name)
            m.register_uri(**data)
        return m
