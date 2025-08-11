from rest_framework import serializers
from .permission import PermissionSerializer
from ..drf.serializers import RelatedSerializerField
from ..models import Role


class RoleSerializer(serializers.ModelSerializer):
    permissions = RelatedSerializerField(PermissionSerializer, many=True)

    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']
