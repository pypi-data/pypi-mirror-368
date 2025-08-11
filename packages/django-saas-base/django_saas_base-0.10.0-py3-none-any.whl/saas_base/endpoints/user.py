from rest_framework.request import Request
from rest_framework.response import Response
from ..drf.views import AuthenticatedEndpoint
from ..serializers.user import (
    UserSerializer,
    UserPasswordSerializer,
)

__all__ = [
    'UserEndpoint',
    'UserPasswordEndpoint',
]


class UserEndpoint(AuthenticatedEndpoint):
    resource_scopes = ['user', 'user:profile']
    serializer_class = UserSerializer

    def get(self, request: Request):
        """Retrieve current user information."""
        serializer: UserSerializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """Update current user information."""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserPasswordEndpoint(AuthenticatedEndpoint):
    resource_scopes = ['user:password']
    serializer_class = UserPasswordSerializer

    def post(self, request: Request, *args, **kwargs):
        """Update current user's password"""
        serializer: UserPasswordSerializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=204)
