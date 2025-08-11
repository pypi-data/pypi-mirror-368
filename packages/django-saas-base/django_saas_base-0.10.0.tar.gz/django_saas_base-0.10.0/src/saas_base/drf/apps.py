from django.apps import AppConfig


class RestFrameworkConfig(AppConfig):
    name = 'saas_base.drf'

    def ready(self):
        from django.apps import apps
        from django.utils.module_loading import autodiscover_modules

        try:
            apps.get_app_config('drf_spectacular')
            autodiscover_modules('spectacular_schema')
        except LookupError:
            pass
