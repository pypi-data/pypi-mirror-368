from rest_framework.mixins import ListModelMixin
from rest_framework.request import Request
from ..drf.views import Endpoint
from ..models import Role
from ..serializers.role import RoleSerializer


__all__ = ['RoleListEndpoint']


class RoleListEndpoint(ListModelMixin, Endpoint):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()
    permission_classes = []
    pagination_class = None

    def get(self, request: Request, *args, **kwargs):
        """Show all supported Roles."""
        return self.list(request, *args, **kwargs)
