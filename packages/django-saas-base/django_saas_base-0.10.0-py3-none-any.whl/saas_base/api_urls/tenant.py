from django.urls import path
from ..endpoints.tenant import (
    SelectedTenantEndpoint,
    CurrentMemberEndpoint,
)

urlpatterns = [
    path('', SelectedTenantEndpoint.as_view()),
    path('member/', CurrentMemberEndpoint.as_view()),
]
