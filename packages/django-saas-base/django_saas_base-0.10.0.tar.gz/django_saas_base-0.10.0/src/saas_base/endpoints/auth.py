from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth import login, logout
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from ..models import Member
from ..drf.views import Endpoint
from ..settings import saas_settings
from ..security import check_security_rules
from ..serializers.auth import (
    EmailCode,
    SignupRequestCodeSerializer,
    SignupCreateUserSerializer,
    SignupConfirmCodeSerializer,
    SignupConfirmPasswordSerializer,
)
from ..serializers.password import PasswordLoginSerializer
from ..signals import after_signup_user, after_login_user
from ..mail import SendEmailMixin


__all__ = [
    'SignupRequestEndpoint',
    'SignupConfirmEndpoint',
    'PasswordLogInEndpoint',
    'LogoutEndpoint',
]


class SignupRequestEndpoint(SendEmailMixin, Endpoint):
    email_template_id = 'signup_code'
    email_subject = _('Signup Request')
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def get_serializer_class(self):
        if saas_settings.SIGNUP_REQUEST_CREATE_USER:
            return SignupCreateUserSerializer
        return SignupRequestCodeSerializer

    def post(self, request: Request):
        """Send a sign-up code to user's email address."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj: EmailCode = serializer.save()
        # check bad request rules
        check_security_rules(saas_settings.SIGNUP_SECURITY_RULES, request)

        self.send_email([obj.recipient()], code=obj.code)
        return Response(status=204)


class SignupConfirmEndpoint(Endpoint):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def get_serializer_class(self):
        if saas_settings.SIGNUP_REQUEST_CREATE_USER:
            return SignupConfirmCodeSerializer
        return SignupConfirmPasswordSerializer

    def post(self, request: Request):
        """Register a new user and login."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # update related membership
        Member.objects.filter(email=user.email).update(user=user, status=Member.InviteStatus.WAITING)
        after_signup_user.send(
            self.__class__,
            user=user,
            request=request,
            strategy='password',
        )
        return Response({'next': settings.LOGIN_REDIRECT_URL})


class PasswordLogInEndpoint(Endpoint):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]
    serializer_class = PasswordLoginSerializer

    def post(self, request: Request):
        """Login a user with the given username and password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request._request, user)

        after_login_user.send(
            self.__class__,
            user=user,
            request=request,
            strategy='password',
        )
        return Response({'next': settings.LOGIN_REDIRECT_URL})


class LogoutEndpoint(Endpoint):
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request):
        """Clear the user session and log the user out."""
        logout(request._request)
        return Response({'next': settings.LOGIN_URL})
