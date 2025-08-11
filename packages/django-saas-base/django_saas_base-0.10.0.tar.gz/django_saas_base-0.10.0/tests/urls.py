from django.urls import path, include
from drf_spectacular.views import SpectacularJSONAPIView


urlpatterns = [
    path('m/', include('saas_base.api_urls.all')),
    path('tenant/<tenant_id>/members/', include('saas_base.api_urls.members')),
    path('schema/openapi', SpectacularJSONAPIView.as_view(), name='schema'),
]
