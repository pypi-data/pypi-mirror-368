from rest_framework import serializers
from .permission import PermissionSerializer
from ..drf.serializers import RelatedSerializerField
from ..models import Group


class GroupSerializer(serializers.ModelSerializer):
    permissions = RelatedSerializerField(PermissionSerializer, many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'managed']
