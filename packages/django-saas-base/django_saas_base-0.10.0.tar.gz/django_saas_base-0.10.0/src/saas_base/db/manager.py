import typing as t
import hashlib
import logging
import uuid

from django.db.models import Model, Manager, UUIDField
from django.db.models.signals import (
    class_prepared,
    post_save,
    post_delete,
)
from .cache import cache

__all__ = ['CachedManager']

logger = logging.getLogger(__name__)

M = t.TypeVar('M', bound=Model)


class CachedManager(Manager, t.Generic[M]):
    db_cache = cache
    natural_key: t.List[str] = []
    cache_ttl: int = 300
    cache_version = 1
    query_select_related: t.List[str] = []

    def contribute_to_class(self, model: t.Type[M], name: str):
        super().contribute_to_class(model, name)
        class_prepared.connect(self.__manage_cache, sender=model)

    def get_many_from_cache(self, pk_set: t.List[t.Any]) -> t.Dict[t.Any, M]:
        key_map = {self.__get_lookup_cache_key(pk=pk): pk for pk in pk_set}
        results = self.db_cache.get_many(key_map.keys(), version=self.cache_version)

        found = {}
        missed = []
        for key in key_map:
            if key not in results:
                missed.append(key_map[key])
            else:
                found[key_map[key]] = results[key]

        if missed:
            queryset = self.filter(pk__in=missed).select_related(*self.query_select_related).all()
            for instance in queryset:
                self.__post_save(instance)
                found[instance.pk] = instance
        return found

    def get_from_cache_by_pk(self, pk: t.Any) -> M:
        key = self.__get_lookup_cache_key(pk=pk)
        instance = self.__get_from_cache_or_raise(key)
        if instance:
            instance._state.db = self.db
            return instance

        try:
            if self.query_select_related:
                instance = self.select_related(*self.query_select_related).get(pk=pk)
            else:
                instance = self.get(pk=pk)
        except self.model.DoesNotExist:
            self.__set_not_exist_cache(key)
            raise self.model.DoesNotExist

        self.__post_save(instance)
        return instance

    def get_from_cache_by_natural_key(self, *args) -> M:
        kwargs = dict(zip(self.natural_key, args))
        key = self.__get_lookup_cache_key(**kwargs)
        pk_val = self.__get_from_cache_or_raise(key)
        if pk_val:
            return self.get_from_cache_by_pk(pk_val)

        try:
            instance = self.get_from_db_by_natural_key(**kwargs)
        except self.model.DoesNotExist:
            self.__set_not_exist_cache(key)
            raise self.model.DoesNotExist

        self.__post_save(instance)
        return instance

    def get_from_db_by_natural_key(self, **kwargs) -> M:
        if self.query_select_related:
            instance = self.select_related(*self.query_select_related).get(**kwargs)
        else:
            instance = self.get(**kwargs)
        return instance

    def purge(self, pk_value):
        key = self.__get_lookup_cache_key(pk=pk_value)
        self.db_cache.delete(key, version=self.cache_version)

    def __manage_cache(self, sender, **kwargs):
        post_save.connect(self.__post_save, sender=sender, weak=False)
        post_delete.connect(self.__post_delete, sender=sender, weak=False)

    def __get_from_cache_or_raise(self, key: str):
        value = self.db_cache.get(key, version=self.cache_version)
        if value == '__none__':
            raise self.model.DoesNotExist
        return value

    def __set_not_exist_cache(self, key: str):
        self.db_cache.set(
            key=key,
            value='__none__',
            timeout=self.cache_ttl,
            version=self.cache_version,
        )

    def __get_lookup_cache_key(self, **kwargs) -> str:
        key = make_key(self.model, kwargs)
        return f'db:{self.model._meta.db_table}:{key}'

    def __get_natural_cache_key(self, instance: M) -> str:
        natural_fields = {key: value_for_field(instance, key) for key in self.natural_key}
        return self.__get_lookup_cache_key(**natural_fields)

    def __post_save(self, instance, **kwargs):
        if not kwargs.get('created'):
            _natural_cache_key = self.db_cache.get(
                self.__get_lookup_cache_key(__track=instance.pk),
                version=self.cache_version,
            )
        else:
            _natural_cache_key = None

        natural_cache_key = self.__get_natural_cache_key(instance)
        if _natural_cache_key and _natural_cache_key != natural_cache_key:
            self.db_cache.delete(_natural_cache_key, version=self.cache_version)

        to_save = {
            natural_cache_key: instance.pk,
            self.__get_lookup_cache_key(__track=instance.pk): natural_cache_key,
        }
        self.db_cache.set_many(to_save, timeout=self.cache_ttl, version=self.cache_version)

        # Ensure we don't serialize the database into the cache
        db = instance._state.db
        instance._state.db = None

        # store actual object
        try:
            self.db_cache.set(
                key=self.__get_lookup_cache_key(pk=instance.pk),
                value=instance,
                timeout=self.cache_ttl,
                version=self.cache_version,
            )
        except Exception as e:
            logger.error(e, exc_info=True)

        # recover database on instance
        instance._state.db = db

    def __post_delete(self, instance, **kwargs):
        to_delete = [
            self.__get_lookup_cache_key(pk=instance.pk),
            self.__get_natural_cache_key(instance),
            self.__get_lookup_cache_key(__track=instance.pk),
        ]
        self.db_cache.delete_many(to_delete, version=self.cache_version)


def make_key(cls: Model, kwargs: t.Mapping[str, t.Union[Model, int, str]]) -> str:
    fields = []
    for k, v in sorted(kwargs.items()):
        if k == 'pk':
            # convert pk to its real name
            k = str(cls._meta.pk.name)
            if isinstance(v, str) and isinstance(cls._meta.pk, UUIDField):
                v = v.replace('-', '')
        if isinstance(v, Model):
            v = v.pk
        if isinstance(v, uuid.UUID):
            v = v.hex
        fields.append(f'{k}={v}')
    return hashlib.md5('&'.join(fields).encode('utf-8')).hexdigest()


def value_for_field(instance: M, key: str) -> t.Any:
    field = instance._meta.get_field(key)
    return getattr(instance, field.attname)
