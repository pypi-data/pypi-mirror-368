from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.mixins import (
    ListModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.throttling import UserRateThrottle
from ..drf.views import AuthenticatedEndpoint
from ..models import UserEmail
from ..mail import SendEmailMixin
from ..serializers.user_email import (
    UserEmailSerializer,
    AddEmailRequestSerializer,
    AddEmailConfirmSerializer,
)

__all__ = [
    'UserEmailListEndpoint',
    'UserEmailItemEndpoint',
    'AddUserEmailRequestEndpoint',
    'AddUserEmailConfirmEndpoint',
]


class UserEmailListEndpoint(ListModelMixin, AuthenticatedEndpoint):
    resource_scopes = ['user:email']
    pagination_class = None
    serializer_class = UserEmailSerializer

    def get_queryset(self):
        return UserEmail.objects.filter(user=self.request.user).all()

    def get(self, request: Request, *args, **kwargs):
        """List all the current user's emails."""
        return self.list(request, *args, **kwargs)


class UserEmailItemEndpoint(RetrieveModelMixin, DestroyModelMixin, AuthenticatedEndpoint):
    resource_scopes = ['user:email']
    pagination_class = None
    serializer_class = UserEmailSerializer
    queryset = UserEmail.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).all()

    def get(self, request: Request, *args, **kwargs):
        """Retrieve the current user's emails with the given uuid.'"""
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request: Request, *args, **kwargs):
        """Set this email to be the primary email address."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, *args, **kwargs):
        """List all the current user's emails."""
        return self.destroy(request, *args, **kwargs)


class AddUserEmailRequestEndpoint(SendEmailMixin, AuthenticatedEndpoint):
    resource_scopes = ['user:email']
    email_template_id = 'add_email'
    email_subject = _('Add new email')

    throttle_classes = [UserRateThrottle]
    serializer_class = AddEmailRequestSerializer

    def post(self, request: Request):
        """Send a request of authorization code for linking the account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        self.send_email([obj.recipient()], code=obj.code, user=obj.user)
        return Response(status=204)


class AddUserEmailConfirmEndpoint(AuthenticatedEndpoint):
    resource_scopes = ['user:email']
    throttle_classes = [UserRateThrottle]
    serializer_class = AddEmailConfirmSerializer

    def post(self, request: Request):
        """Reset password of a user with the given code."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = UserEmailSerializer(obj).data
        return Response(data)
