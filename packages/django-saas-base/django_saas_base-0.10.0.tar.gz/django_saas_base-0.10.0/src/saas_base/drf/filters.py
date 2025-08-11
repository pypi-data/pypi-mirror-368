from django.conf import settings
from rest_framework.fields import BooleanField
from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ValidationError
from .errors import BadRequest
from ..settings import saas_settings

__all__ = [
    'TenantIdFilter',
    'IncludeFilter',
    'ChoiceFilter',
]


class TenantIdFilter(BaseFilterBackend):
    tenant_id_field = 'tenant_id'

    def filter_queryset(self, request, queryset, view):
        query_field = getattr(view, 'tenant_id_field', self.tenant_id_field)

        tenant_id = getattr(request, 'tenant_id', None)
        if not tenant_id:
            raise BadRequest('Missing Tenant ID')

        kwargs = {query_field: tenant_id}
        return queryset.filter(**kwargs)

    def get_schema_operation_parameters(self, view):
        in_header = 'saas_base.middleware.HeaderTenantIdMiddleware' in settings.MIDDLEWARE
        in_path = 'saas_base.middleware.PathTenantIdMiddleware' in settings.MIDDLEWARE

        parameters = []
        if in_header:
            parameters.append(
                {
                    'name': saas_settings.TENANT_ID_HEADER,
                    'required': True,
                    'in': 'header',
                    'schema': {
                        'type': 'string',
                    },
                }
            )

        if in_path:
            parameters.append(
                {
                    'name': 'tenant_id',
                    'required': True,
                    'in': 'path',
                    'schema': {
                        'type': 'string',
                    },
                }
            )

        if len(parameters) == 2:
            parameters[0]['required'] = False
            parameters[0]['description'] = 'Tenant ID (required if not provided in path).'
            parameters[1]['required'] = False
            parameters[1]['description'] = 'Tenant ID (required if not provided in header).'

        return parameters


class IncludeFilter(BaseFilterBackend):
    def get_select_related_fields(self, view):
        return getattr(view, 'include_select_related_fields', [])

    def get_prefetch_related_fields(self, view):
        return getattr(view, 'include_prefetch_related_fields', [])

    def get_include_terms(self, request):
        params = request.query_params.get('include', '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        return params.split()

    def filter_queryset(self, request, queryset, view):
        select_related_fields = self.get_select_related_fields(view)
        prefetch_related_fields = self.get_prefetch_related_fields(view)
        if not select_related_fields and not prefetch_related_fields:
            return queryset

        include_terms = self.get_include_terms(request)
        if not include_terms:
            return queryset

        if include_terms == ['all']:
            include_terms = select_related_fields + prefetch_related_fields

        for field in include_terms:
            if field in select_related_fields:
                queryset = queryset.select_related(field)
            elif field in prefetch_related_fields:
                queryset = queryset.prefetch_related(field)
                relations = [key for key in prefetch_related_fields if key.startswith(f'{field}__')]
                queryset = queryset.prefetch_related(*relations)

        request.include_terms = include_terms
        return queryset

    def get_schema_operation_parameters(self, view):
        select_related_fields = self.get_select_related_fields(view)
        prefetch_related_fields = self.get_prefetch_related_fields(view)
        related_fields = ['all'] + select_related_fields + prefetch_related_fields
        desc = ', '.join([f'`"{name}"`' for name in related_fields if '__' not in name])
        return [
            {
                'name': 'include',
                'required': False,
                'in': 'query',
                'description': f'Include related fields of {desc}',
                'schema': {
                    'type': 'string',
                },
            },
        ]


class ChoiceFilter(BaseFilterBackend):
    default_choice_filter_fields = ['status']

    def get_choice_filter_fields(self, view):
        return getattr(view, 'choice_filter_fields', self.default_choice_filter_fields)

    def get_choice_filter_terms(self, view, request):
        params = {}
        for key in self.get_choice_filter_fields(view):
            value = request.query_params.get(key, '')
            if value:
                params[key] = value
        return params

    def filter_queryset(self, request, queryset, view):
        terms = self.get_choice_filter_terms(view, request)
        if not terms:
            return queryset

        serializer_cls = view.get_serializer_class()
        serializer = serializer_cls()
        for key in terms:
            field = serializer.fields[key]
            try:
                value = field.to_internal_value(terms[key])
            except ValidationError:
                continue
            queryset = queryset.filter(**{key: value})
        return queryset

    def get_schema_operation_parameters(self, view):
        choice_filter_fields = self.get_choice_filter_fields(view)
        serializer_cls = view.get_serializer_class()
        serializer = serializer_cls()
        schema = []

        for key in choice_filter_fields:
            field = serializer.fields[key]
            if isinstance(field, BooleanField):
                schema.append(
                    {
                        'name': key,
                        'required': False,
                        'in': 'query',
                        'schema': {
                            'type': 'boolean',
                        },
                    }
                )
            else:
                choices = [field.to_representation(v) for v in field.choices]
                schema.append(
                    {
                        'name': key,
                        'required': False,
                        'in': 'query',
                        'schema': {
                            'type': 'string',
                            'enum': choices,
                        },
                    }
                )
        return schema
