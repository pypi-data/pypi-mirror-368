from django.core.cache import caches, BaseCache
from django.utils.connection import ConnectionProxy
from ..settings import saas_settings

cache: BaseCache = ConnectionProxy(caches, saas_settings.DB_CACHE_ALIAS)  # type: ignore[assignment]


__all__ = ['cache']
