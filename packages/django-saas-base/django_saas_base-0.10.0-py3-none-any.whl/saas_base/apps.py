from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate
from .permissions import create_permissions

if not hasattr(settings, 'SAAS_TENANT_MODEL'):
    setattr(settings, 'SAAS_TENANT_MODEL', 'saas_base.Tenant')


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saas_base'
    verbose_name = 'SaaS'

    def ready(self):
        post_migrate.connect(create_permissions)
