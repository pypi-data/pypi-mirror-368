from django.utils.translation import gettext as _
from django.contrib.auth import password_validation, authenticate
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .email_code import (
    EmailCodeRequestSerializer,
    EmailCodeConfirmSerializer,
    RetrieveUserEmailMixin,
)
from ..models import UserEmail

PASSWORD_CODE = 'saas:password_code'


class PasswordLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    @staticmethod
    def invalid_errors():
        errors = {'password': [_('Invalid username or password.')]}
        return ValidationError(errors)

    def create(self, validated_data):
        request = self.context['request']
        user = authenticate(request=request, **validated_data)
        if not user:
            raise self.invalid_errors()
        return user

    def update(self, instance, validated_data):
        raise RuntimeError('This method is not allowed.')


class PasswordForgetSerializer(RetrieveUserEmailMixin, EmailCodeRequestSerializer):
    CACHE_PREFIX = PASSWORD_CODE

    def create(self, validated_data) -> UserEmail:
        user_email = validated_data['email']
        return user_email


class PasswordResetSerializer(RetrieveUserEmailMixin, EmailCodeConfirmSerializer):
    CACHE_PREFIX = PASSWORD_CODE
    password = serializers.CharField(required=True)

    def validate_password(self, raw_password):
        password_validation.validate_password(raw_password)
        return raw_password

    def create(self, validated_data):
        obj: UserEmail = validated_data['email']
        user_id = validated_data['code']

        if not user_id or obj.user_id != user_id:
            raise ValidationError({'code': [_('Code does not match or expired.')]})

        raw_password = validated_data['password']
        user: AbstractUser = obj.user
        user.set_password(raw_password)
        user.save()
        return obj
