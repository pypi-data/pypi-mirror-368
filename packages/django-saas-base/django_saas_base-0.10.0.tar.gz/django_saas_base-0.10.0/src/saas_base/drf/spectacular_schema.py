from typing import TYPE_CHECKING
from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_array_type

if TYPE_CHECKING:
    from drf_spectacular.openapi import AutoSchema
    from drf_spectacular.utils import Direction


class ChoiceFieldFix(OpenApiSerializerFieldExtension):
    target_class = 'saas_base.drf.serializers.ChoiceField'

    def map_serializer_field(self, auto_schema: 'AutoSchema', direction: 'Direction'):
        choices = list(self.target.choices.values())
        return {'type': 'string', 'enum': choices}


class RelatedSerializerField(OpenApiSerializerFieldExtension):
    target_class = 'saas_base.drf.serializers.RelatedSerializerField'

    def map_serializer_field(self, auto_schema: 'AutoSchema', direction: 'Direction'):
        if direction == 'response':
            schema = auto_schema._map_serializer(self.target.serializer_cls, direction, bypass_extensions=True)
        else:
            model = self.target.serializer_cls.Meta.model
            pk_field = model._meta.pk
            schema = auto_schema._map_model_field(pk_field, direction)

        if self.target.many:
            schema = build_array_type(schema)
        return schema
