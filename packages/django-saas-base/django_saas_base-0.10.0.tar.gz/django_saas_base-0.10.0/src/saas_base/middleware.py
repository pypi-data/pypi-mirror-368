from django.utils.functional import SimpleLazyObject
from django.conf import settings
from .settings import saas_settings
from .models import get_tenant_model

__all__ = [
    'TenantMiddleware',
    'ConfiguredTenantIdMiddleware',
    'HeaderTenantIdMiddleware',
    'PathTenantIdMiddleware',
    'SessionTenantIdMiddleware',
]
TenantModel = get_tenant_model()


class TenantMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    @staticmethod
    def get_tenant(request):
        if not hasattr(request, '_cached_tenant'):
            TenantModel = get_tenant_model()
            tenant_id = getattr(request, 'tenant_id', None)
            if not tenant_id:
                return None
            try:
                tenant = TenantModel.objects.get_from_cache_by_pk(tenant_id)
                request._cached_tenant = tenant
            except TenantModel.DoesNotExist:
                return None
        return getattr(request, '_cached_tenant', None)

    def __call__(self, request):
        request.tenant = SimpleLazyObject(lambda: self.get_tenant(request))
        response = self.get_response(request)
        return response


class ConfiguredTenantIdMiddleware:
    SETTING_KEY = 'SAAS_TENANT_ID'

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant_id = getattr(settings, self.SETTING_KEY, None)
        return self.get_response(request)


class HeaderTenantIdMiddleware:
    HTTP_HEADER = saas_settings.TENANT_ID_HEADER

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, 'tenant_id', None):
            return self.get_response(request)

        tenant_id = request.headers.get(self.HTTP_HEADER)
        request.tenant_id = TenantModel._meta.pk.to_python(tenant_id)
        return self.get_response(request)


class PathTenantIdMiddleware:
    FIELD_KEY = 'tenant_id'

    def __init__(self, get_response=None):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if getattr(request, 'tenant_id', None):
            return
        tenant_id = view_kwargs.get(self.FIELD_KEY)
        request.tenant_id = TenantModel._meta.pk.to_python(tenant_id)

    def __call__(self, request):
        return self.get_response(request)


class SessionTenantIdMiddleware:
    FIELD_KEY = 'tenant_id'

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, 'tenant_id', None):
            return self.get_response(request)

        tenant_id = request.session.get(self.FIELD_KEY)
        request.tenant_id = TenantModel._meta.pk.to_python(tenant_id)
        return self.get_response(request)
