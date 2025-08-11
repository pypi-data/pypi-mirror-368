from rest_framework.request import Request
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from ..drf.filters import IncludeFilter, ChoiceFilter
from ..drf.views import AuthenticatedEndpoint
from ..models import Member
from ..serializers.member import UserMembershipSerializer

__all__ = [
    'UserMemberListEndpoint',
    'UserMemberItemEndpoint',
]


class UserMemberListEndpoint(ListModelMixin, AuthenticatedEndpoint):
    serializer_class = UserMembershipSerializer
    queryset = Member.objects.select_related('tenant').all()
    filter_backends = [IncludeFilter, ChoiceFilter]
    choice_filter_fields = ['status']
    include_prefetch_related_fields = ['groups', 'permissions', 'groups__permissions']
    resource_scopes = ['user', 'user:member']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get(self, request: Request, *args, **kwargs):
        """List all the current user's tenants."""
        return self.list(request, *args, **kwargs)


class UserMemberItemEndpoint(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, AuthenticatedEndpoint):
    serializer_class = UserMembershipSerializer
    queryset = Member.objects.all()
    resource_scopes = ['user', 'user:member']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get(self, request: Request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request: Request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request: Request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
