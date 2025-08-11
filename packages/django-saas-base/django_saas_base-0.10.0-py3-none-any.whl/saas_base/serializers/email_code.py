import random
import string
from email.utils import formataddr
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from ..models import UserEmail


ERRORS = {
    'code': _('Code does not match or expired.'),
    'exist_email': _('This email address is already associated with an existing account.'),
    'invalid_email': _('This email address is not associated with your account.'),
}


class EmailCode:
    def __init__(self, email: str, code: str, user=None):
        self.email = email
        self.code = code
        self.user = user

    def recipient(self):
        if self.user:
            return formataddr((self.user.username, self.email))
        return self.email


class EmailCodeRequestSerializer(serializers.Serializer):
    CACHE_PREFIX = 'saas:email_code'
    email = serializers.EmailField(required=True)

    def save_auth_code(self, value):
        email = self.validated_data['email']
        code = ''.join(random.sample(string.ascii_uppercase, 6))
        cache_key = f'{self.CACHE_PREFIX}:{email}:{code}'
        cache.set(cache_key, value, timeout=300)
        return code


class EmailCodeConfirmSerializer(serializers.Serializer):
    CACHE_PREFIX = 'saas:email_code'
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, max_length=6)

    def fail_code(self):
        raise ValidationError(ERRORS['code'])

    def validate_code(self, code: str):
        email = self.initial_data['email']
        code = code.upper()
        cache_key = f'{self.CACHE_PREFIX}:{email}:{code}'
        value: str = cache.get(cache_key)
        if not value:
            self.fail_code()

        cache.delete(cache_key)
        return value


class NewUserEmailMixin:
    def validate_email(self, email: str):
        email = UserEmail.objects.normalize_email(email)
        try:
            UserEmail.objects.get(email=email)
            raise ValidationError(ERRORS['exist_email'])
        except UserEmail.DoesNotExist:
            return email


class RetrieveUserEmailMixin(serializers.Serializer):
    def validate_email(self, email: str):
        email = UserEmail.objects.normalize_email(email)
        try:
            user_email = UserEmail.objects.select_related('user').get(email=email)
        except UserEmail.DoesNotExist:
            raise ValidationError(ERRORS['invalid_email'])
        return user_email
