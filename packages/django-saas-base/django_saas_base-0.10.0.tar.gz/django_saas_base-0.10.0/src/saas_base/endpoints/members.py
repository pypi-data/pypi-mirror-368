from email.utils import formataddr
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.mixins import (
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from ..settings import saas_settings
from ..drf.views import TenantEndpoint
from ..drf.decorators import resource_permissions
from ..drf.filters import TenantIdFilter, IncludeFilter, ChoiceFilter
from ..mail import SendEmailMixin
from ..serializers.member import (
    MemberSerializer,
    MemberInviteSerializer,
    MemberDetailSerializer,
)
from ..models import Member
from ..signals import member_invited

__all__ = [
    'MemberListEndpoint',
    'MemberItemEndpoint',
]


class MemberListEndpoint(SendEmailMixin, ListModelMixin, TenantEndpoint):
    email_template_id = 'invite_member'
    email_subject = _("You've Been Invited to Join %s")

    serializer_class = MemberSerializer
    filter_backends = [TenantIdFilter, IncludeFilter, ChoiceFilter]
    queryset = Member.objects.all()

    resource_name = 'tenant'
    resource_scopes = ['tenant', 'tenant:member']

    choice_filter_fields = ['status', 'is_staff']
    include_select_related_fields = ['user']
    include_prefetch_related_fields = ['groups', 'permissions', 'groups__permissions']

    def get_email_subject(self):
        return self.email_subject % str(self.request.tenant)

    def get(self, request: Request, *args, **kwargs):
        """List all members in the tenant."""
        return self.list(request, *args, **kwargs)

    @resource_permissions('tenant.admin')
    def post(self, request: Request, *args, **kwargs):
        """Invite a member to join the tenant."""
        tenant_id = self.get_tenant_id()
        context = self.get_serializer_context()
        serializer = MemberInviteSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        member = serializer.save(tenant_id=tenant_id, inviter=request.user)

        member_invited.send(self.__class__, member=member, request=request)
        if member.status != Member.InviteStatus.ACTIVE:
            if member.name:
                recipient = formataddr((member.name, member.email))
            else:
                recipient = member.email
            self.send_email(
                [recipient],
                inviter=request.user,
                member=member,
                tenant=request.tenant,
                invite_link=saas_settings.MEMBER_INVITE_LINK % str(member.id),
            )
        data = MemberDetailSerializer(member).data
        return Response(data)


class MemberItemEndpoint(UpdateModelMixin, DestroyModelMixin, TenantEndpoint):
    serializer_class = MemberDetailSerializer
    queryset = Member.objects.all()
    resource_name = 'tenant'
    resource_scopes = ['tenant', 'tenant:member']

    def get(self, request: Request, *args, **kwargs):
        """Retrieve the information of a member."""
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.prefetch_related('groups', 'permissions', 'groups__permissions')
        member = self.get_object_or_404(queryset, pk=kwargs['pk'])
        self.check_object_permissions(request, member)
        serializer = self.get_serializer(member)
        return Response(serializer.data)

    @resource_permissions('tenant.admin')
    def patch(self, request: Request, *args, **kwargs):
        """Update a member's permissions and groups."""
        return self.partial_update(request, *args, **kwargs)

    @resource_permissions('tenant.admin')
    def delete(self, request: Request, *args, **kwargs):
        """Remove a member from the tenant."""
        return self.destroy(request, *args, **kwargs)
