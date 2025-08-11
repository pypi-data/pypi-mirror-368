from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, ListModelMixin
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from ..drf.views import AuthenticatedEndpoint, TenantEndpoint
from ..models import get_tenant_model, Member
from ..serializers.tenant import TenantSerializer
from ..serializers.member import MemberDetailSerializer

__all__ = [
    'SelectedTenantEndpoint',
    'CurrentMemberEndpoint',
    'TenantListEndpoint',
]


class SelectedTenantEndpoint(RetrieveModelMixin, TenantEndpoint):
    serializer_class = TenantSerializer
    resource_name = 'tenant'
    tenant_id_field = 'pk'

    def get_queryset(self):
        return get_tenant_model().objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = self.get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request: Request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CurrentMemberEndpoint(RetrieveModelMixin, TenantEndpoint):
    queryset = Member.objects.all()
    serializer_class = MemberDetailSerializer
    resource_name = 'tenant'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        return self.get_object_or_404(queryset, user=self.request.user)

    def get(self, request: Request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TenantListEndpoint(CreateModelMixin, ListModelMixin, AuthenticatedEndpoint):
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated] + api_settings.DEFAULT_PERMISSION_CLASSES

    def get_queryset(self):
        return get_tenant_model().objects.filter(owner=self.request.user).all()

    def get(self, request: Request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request: Request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
