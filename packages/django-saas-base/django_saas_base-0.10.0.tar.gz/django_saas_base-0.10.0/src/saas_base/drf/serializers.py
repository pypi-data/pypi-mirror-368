import re
import typing as t
from collections import OrderedDict

from django.db.models import QuerySet
from rest_framework.validators import ValidationError
from rest_framework.fields import Field, ChoiceField as _ChoiceField
from rest_framework.serializers import ModelSerializer as _ModelSerializer


__all__ = [
    'ChoiceField',
    'RelatedSerializerField',
    'ModelSerializer',
]


class ChoiceField(_ChoiceField):
    """Rewrite this fields to support (int, str) choices."""

    def __init__(self, choices, **kwargs):
        super().__init__(choices, **kwargs)

        self.int_str_choices: t.Dict[int, str] = {}
        self.str_int_choices: t.Dict[str, int] = {}
        if choices:
            self._set_int_str_choices(choices)

    def _set_int_str_choices(self, choices: t.List[t.Tuple[int, str]]):
        int_str_choices: t.Dict[int, str] = {}
        str_int_choices: t.Dict[str, int] = {}
        for choice in choices:
            if len(choice) == 2 and isinstance(choice[0], int) and _is_lower_string(choice[1]):
                int_str_choices[choice[0]] = choice[1]
                str_int_choices[choice[1]] = choice[0]
            else:
                return
        self.int_str_choices = int_str_choices
        self.str_int_choices = str_int_choices

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''

        if self.str_int_choices:
            try:
                return self.str_int_choices[str(data)]
            except KeyError:
                self.fail('invalid_choice', input=data)

        try:
            return self.choice_strings_to_values[str(data)]
        except KeyError:
            self.fail('invalid_choice', input=data)

    def to_representation(self, value):
        if value in ('', None):
            return value

        if self.int_str_choices:
            return self.int_str_choices[value]

        return self.choice_strings_to_values.get(str(value), value)


class RelatedSerializerField(Field):
    def __init__(self, serializer_cls, **kwargs):
        self.serializer_cls = serializer_cls
        self.many = kwargs.pop('many', False)
        super().__init__(**kwargs)

    def to_representation(self, value: QuerySet):
        return self.serializer_cls(value, many=self.many).data

    def to_internal_value(self, data):
        model = self.serializer_cls.Meta.model
        if self.many and not isinstance(data, list):
            raise ValidationError(f'Expected a list of {model.__name__} IDs.')

        if self.many:
            return model.objects.filter(pk__in=data)
        try:
            return model.objects.get(pk=data)
        except model.DoesNotExist:
            raise ValidationError(f'Invalid {model.__name__} ID.')


class ModelSerializer(_ModelSerializer):
    serializer_choice_field = ChoiceField

    @property
    def _readable_fields(self):
        request_include_fields = getattr(self.Meta, 'request_include_fields', [])
        if not request_include_fields:
            for field in self.fields.values():
                if not field.write_only:
                    yield field
        else:
            include_terms = self.context.get('include_fields', [])
            if not include_terms:
                request = self.context.get('request')
                if request:
                    include_terms = getattr(request, 'include_terms', [])

            for field in self.fields.values():
                if field.field_name in request_include_fields and field.field_name not in include_terms:
                    continue

                if not field.write_only:
                    yield field

    def get_fields(self):
        fields = super().get_fields()
        flatten_fields = getattr(self.Meta, 'flatten_fields', None)
        if flatten_fields:
            return _make_flatten_fields(fields, flatten_fields)
        return fields


def _make_flatten_fields(form: OrderedDict, flatten: t.List[str]):
    for source in flatten:
        serializer: t.Any = form.pop(source, None)
        if serializer:
            fields = serializer.get_fields()
            for name in fields:
                field = fields[name]
                if field.source:
                    field.source = f'{source}.{field.source}'
                else:
                    field.source = f'{source}.{name}'
                if name in form:
                    form[f'{source}_{name}'] = field
                else:
                    form[name] = field
    return form


def _is_lower_string(s: str):
    return isinstance(s, str) and bool(re.match(r'^[0-9a-z-_]+$', s))
