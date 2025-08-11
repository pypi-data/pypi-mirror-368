import requests
from abc import ABCMeta, abstractmethod
from rest_framework.request import Request
from .ip import get_client_ip


class Rule(metaclass=ABCMeta):
    DEFAULT_RESPONSE_FIELD: str = 'email'

    def __init__(self, **options):
        self.options = options

    def get_response_field_value(self, request: Request):
        response_field = self.options.get(
            'response_field',
            self.DEFAULT_RESPONSE_FIELD,
        )
        return request.data.get(response_field)

    @abstractmethod
    def bad_request(self, request: Request):
        pass


class BlockedEmailDomains(Rule):
    def bad_request(self, request: Request):
        blocked_list = self.options.get('domains')
        email = self.get_response_field_value(request)
        return blocked_list and email.endswith(tuple([f'@{s}' for s in blocked_list]))


class TooManyDots(Rule):
    MAX_DOT_COUNT = 4

    def bad_request(self, request: Request):
        max_dot_count = self.options.get('count', self.MAX_DOT_COUNT)
        email = self.get_response_field_value(request)
        name = email.split('@')[0]
        return name.count('.') > max_dot_count


class Turnstile(Rule):
    API_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    DEFAULT_RESPONSE_FIELD = 'cf-turnstile-response'

    def bad_request(self, request: Request):
        token = self.get_response_field_value(request)
        if not token:
            return True

        secret = self.options.get('secret')
        ip = get_client_ip(request)
        data = {'secret': secret, 'remoteip': ip, 'response': token}
        resp = requests.post(self.API_URL, data=data, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return not data.get('success')
